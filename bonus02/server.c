#ifndef __SERVER_C
#define __SERVER_C

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <sys/time.h>
#include <sys/types.h>
#include <stdbool.h>
#include <errno.h>
#include <sys/select.h>
#include <sys/time.h>
#include <sys/types.h>
#include <unistd.h>
#include <signal.h>
#include <sys/random.h>
#include "const.h"
#include "err_messages.h"
#include "session.h"
#include "session_set.h"

#define SOCKET_NOT_SET -1
#define FN_ERR -1
#define PROTOCOL_AUTO_CHOICE 0
#define MASTER_SO_NULL 1
#define CLIENT_SO_NULL 2
#define MAX_PENDING_CONNECTIONS 3
#define TIME_OUT 10
#define READ_EOF 0
#define RANDOM_MIN 0
#define RANDOM_MAX 10000

volatile sig_atomic_t running = true;


/**
 * @brief Prepares the client socket array.
 * 
 * @param p_client_socket_fds Pointer to the client socket array
 * @param p_err Pointer to the error flag
 */
void prepare_sockets(int *p_client_socket_fds, int *p_err) {
    int i;
    
    // sanity check
    if (p_client_socket_fds == NULL) {
        *p_err = true;
        return;
    }
    
    for (i = 0; i < MAX_CLIENTS; i++) {
        p_client_socket_fds[i] = SOCKET_NOT_SET;
    }
}

/**
 * @brief Initializes the master socket.
 * 
 * @param fd_master_socket Pointer to the master socket file descriptor
 * @param p_client_socket_fds Pointer to the client socket array
 * @param p_err Pointer to the error flag
 */
void init_master_socket(int *fd_master_socket, int *p_err) {
    *fd_master_socket = socket(AF_INET, SOCK_STREAM, PROTOCOL_AUTO_CHOICE);
    if (*fd_master_socket == SOCKET_NOT_SET) {
        *p_err = true;
        return;
    }
}

/**
 * @brief Sets up the master socket.
 * 
 * @param fd_master_socket Master socket file descriptor
 * @param p_client_socket_fds Pointer to the client socket array
 * @param p_err Pointer to the error flag
 */
void set_up_master_socket(int fd_master_socket, int *p_client_socket_fds, int *p_err) {
    int opt = true;
    int res;

    // sanity check
    if (p_client_socket_fds == NULL) {
        errno = CLIENT_SO_NULL;
        *p_err = true;
        return;
    }
    if (fd_master_socket == 0) {
        errno = MASTER_SO_NULL;
        *p_err = true;
        return;
    }

    // set master socket to allow multiple connections
    res = setsockopt(fd_master_socket, SOL_SOCKET, SO_REUSEADDR, (char *)&opt, sizeof(opt));
    if (res == FN_ERR) {
        *p_err = true;
        close(fd_master_socket);
    }
}

/**
 * @brief Configures the address.
 * 
 * @param p_address Pointer to the address structure
 * @param port Port number
 */
void configure_address(struct sockaddr_in *p_address, int port) {
    memset(p_address, 0, sizeof(*p_address));
    p_address->sin_family = AF_INET;
    p_address->sin_addr.s_addr = inet_addr(SERVER_IP);
    p_address->sin_port = htons(port);
}

/**
 * @brief Adds active sockets.
 * 
 * @param p_client_socket_fds Pointer to the client socket array
 * @param p_read_fds Pointer to the read file descriptor set
 * @return int Highest file descriptor number for the select or SOCKET_NOT_SET
 */
int add_active_sockets(int *p_client_socket_fds, fd_set *p_read_fds) {
    int i;
    int fd_socket;
    int fd_max_val = SOCKET_NOT_SET;

    for (i = 0; i < MAX_CLIENTS; i++) {
        // socket descriptor
        fd_socket = p_client_socket_fds[i];

        // if valid socket descriptor then add to read list
        if (fd_socket > 0) {
            FD_SET(fd_socket, p_read_fds);
        }

        // highest file descriptor number for the select
        if (fd_socket > fd_max_val) {
            fd_max_val = fd_socket;
        }
    }

    return fd_max_val;
}

/**
 * @brief Handles new connection.
 * 
 * @param fd_master_socket Master socket file descriptor
 * @param p_client_socket_fds Pointer to the client socket array
 * @param p_address Pointer to the address structure
 * @param addrlen Length of the address structure
 * @param p_sess_set Pointer to the session set
 * @param p_err Pointer to the error flag
 */
void handle_new_connection(int fd_master_socket, int *p_client_socket_fds, struct sockaddr_in *p_address, int addrlen, session_set *p_sess_set, int *p_err) {
    int i;
    int new_socket;
    session *p_new_session;
    int rd_num = rand() % (RANDOM_MAX - RANDOM_MIN + 1) + RANDOM_MIN;

    new_socket = accept(fd_master_socket, (struct sockaddr *)p_address, (socklen_t*)&addrlen);
    if (new_socket < 0) {
        *p_err = true;
        return;
    }
    printf("New connection:\nsocket fd is %d, ip(%s), port(%d)\n", new_socket, inet_ntoa(p_address->sin_addr), ntohs(p_address->sin_port));

    // create new session for the new connection
    p_new_session = (session *)malloc(sizeof(session));
    init_session(p_new_session, new_socket, rd_num, p_err);
    if (*p_err) {
        fprintf(stderr, "Session initialization failed.\n");
        return;
    }

    // add new socket to array of sockets
    for (i = 0; i < MAX_CLIENTS; i++) {
        //if position is empty
        if (p_client_socket_fds[i] == SOCKET_NOT_SET) {
            p_client_socket_fds[i] = new_socket;
            printf("Adding to list of sockets as %d\n", i);

            // add new session to the session set
            session_set_add(p_sess_set, p_new_session, p_err);
            if (*p_err) {
                fprintf(stderr, "Session set add failed.\n");
            }

            break;
        }

        if (i == MAX_CLIENTS - 1) {
            fprintf(stderr, "Cannot accept more clients.\n");
            close(new_socket);
            *p_err = true;
        }
    }

    free(p_new_session);
    printf("---\n");
}

/**
 * @brief Handles session validation.
 * 
 * @param p_session Pointer to the session
 * @param p_buffer Pointer to the buffer
 * @param fd_socket Client socket file descriptor
 * @param p_client_socket_fds Pointer to the client socket array
 * @param i Index of the client socket
 * @param p_sess_set Pointer to the session set
 * @param p_disconnect Pointer to the disconnect flag
 * @param p_err Pointer to the error flag
 */
void handle_session_authentication(session *p_session, char *p_buffer, int fd_socket, int *p_client_socket_fds, int i, session_set *p_sess_set, bool *p_disconnect, int *p_err) {
    int res;

    res = session_authenticate(p_session, p_buffer, BUFFER_SIZE, p_err);
    if (*p_err) {
        fprintf(stderr, "Session authenticate failed (passed invalid pointer).\n");
        *p_disconnect = true;
    }
    if (!res) {
        printf("Authentication failed.\n");

        memset(p_buffer, 0, BUFFER_SIZE);
        strcpy(p_buffer, "WRONG\n");
        res = send(fd_socket, p_buffer, strlen(p_buffer), 0);
        if (res == FN_ERR) {
            fprintf(stderr, "Send failed.\n");
        }

        *p_disconnect = true;
    }
    else {
        printf("Authentication successful.\n");
        p_session->state = SESSION_STATE_AUTHORIZED;

        memset(p_buffer, 0, BUFFER_SIZE);
        sprintf(p_buffer, "NUM:%d\n", p_session->num);
        res = send(fd_socket, p_buffer, strlen(p_buffer), 0);
        if (res == FN_ERR) {
            fprintf(stderr, "Send failed.\n");
            *p_disconnect = true;
        }
    }
}

/**
 * @brief Handles session validation.
 * 
 * @param p_session Pointer to the session
 * @param p_buffer Pointer to the buffer
 * @param fd_socket Client socket file descriptor
 * @param p_client_socket_fds Pointer to the client socket array
 * @param i Index of the client socket
 * @param p_sess_set Pointer to the session set
 * @param p_err Pointer to the error flag
 */
void handle_session_validation(session *p_session, char *p_buffer, int fd_socket, int *p_client_socket_fds, int i, session_set *p_sess_set, int *p_err) {
    int res;

    res = session_validate(p_session, p_buffer, BUFFER_SIZE, p_err);
    if (*p_err) {
        fprintf(stderr, "Session validate failed (passed invalid pointer).\n");
    }
    if (!res) {
        printf("Validation failed.\n");
        memset(p_buffer, 0, BUFFER_SIZE);
        strcpy(p_buffer, "WRONG\n");
        res = send(fd_socket, p_buffer, strlen(p_buffer), 0);
        if (res == FN_ERR) {
            fprintf(stderr, "Send failed.\n");
        }
    }
    else {
        printf("Validation successful.\n");
        memset(p_buffer, 0, BUFFER_SIZE);
        strcpy(p_buffer, "OK\n");
        res = send(fd_socket, p_buffer, strlen(p_buffer), 0);
        if (res == FN_ERR) {
            fprintf(stderr, "Send failed.\n");
        }

        // clear the buffer
        memset(p_buffer, 0, BUFFER_SIZE);
    }
}

/**
 * @brief Handles client IO.
 * 
 * @param fd_socket Client socket file descriptor
 * @param p_client_socket_fds Pointer to the client socket array
 * @param p_buffer Pointer to the buffer
 * @param i Index of the client socket
 * @param p_address Pointer to the address structure
 * @param p_addrlen Pointer to the length of the address structure
 * @param p_sess_set Pointer to the session set
 * @param p_err Pointer to the error flag
 */
void handle_client_io(int fd_socket, int *p_client_socket_fds, char *p_buffer, int i, struct sockaddr_in *p_address, int *p_addrlen, session_set *p_sess_set, int *p_err) {
    int received_bytes;
    int res;
    bool disconnect = false;
    session *p_session;

    getpeername(fd_socket, (struct sockaddr *)p_address, (socklen_t*)p_addrlen);     // gets information of the client
    printf("Host interaction: ip(%s), port(%d)\n", inet_ntoa(p_address->sin_addr), ntohs(p_address->sin_port));
    
    received_bytes = read(fd_socket, p_buffer, BUFFER_SIZE);
    if (received_bytes == FN_ERR) {
        // clear the buffer
        memset(p_buffer, 0, BUFFER_SIZE);
        *p_err = true;
        return;
    }
    
    res = session_set_contains(p_sess_set, fd_socket, p_err);
    if (*p_err) {
        fprintf(stderr, "Session set contains failed (passed invalid pointer).\n");
    }
    else if (!res) {
        fprintf(stderr, "Session not found in session set (logic error, should not happen).\n");
        *p_err = true;
    }
    
    // somebody disconnected
    if (received_bytes == READ_EOF) {
        printf("Host disconnected\n");
        disconnect = true;
    }
    // message received
    else {
        p_buffer[received_bytes] = '\0';
        p_session = session_set_peek(p_sess_set, fd_socket, p_err);
        if (*p_err) {
            fprintf(stderr, "Session set get failed.\n");
        }
        else if (p_session == NULL) {
            fprintf(stderr, "Session not found in session set (logic error, should not happen).\n");
            *p_err = true;
            disconnect = true;
        }
        else {
            switch (p_session->state) {
                case SESSION_STATE_CONNECTED:
                    handle_session_authentication(p_session, p_buffer, fd_socket, p_client_socket_fds, i, p_sess_set, &disconnect, p_err);
                    if (*p_err) {
                        fprintf(stderr, "Session authentication failed.\n");
                    }
                    break;
                
                case SESSION_STATE_AUTHORIZED:
                    handle_session_validation(p_session, p_buffer, fd_socket, p_client_socket_fds, i, p_sess_set, p_err);
                    if (*p_err) {
                        fprintf(stderr, "Session validation failed.\n");
                    }
                    disconnect = true;
                    break;

                default:
                    break;
            }
        }
    }

    // in production better to handle this outside
    if (disconnect) {
        printf("Closing sockets\n");
        close(fd_socket);
        p_client_socket_fds[i] = SOCKET_NOT_SET;
        session_set_remove(p_sess_set, fd_socket, p_err);
        if (*p_err) {
            fprintf(stderr, "Session set remove failed.\n");
        }
    }

    // clear the buffer
    memset(p_buffer, 0, BUFFER_SIZE);

    printf("---\n");
}

/**
 * @brief Signal handler for SIGINT.
 * 
 * @param sig Signal number
 */
void sigintHandler(int sig) {
    printf("Caught signal %d\n", sig);
    running = (sig_atomic_t) false;
}

////////////////////////////////////////////////////////////////////////////////////////////////////
int main() {
    int i;
    int err = false;
    int res;
    int fd_master_socket, addrlen, fd_socket;
    int p_client_socket_fds[MAX_CLIENTS];
    int fd_max_val;
    struct sockaddr_in address;
    struct timeval time_out;
    char p_buffer[BUFFER_SIZE];
    fd_set read_fds;     //set of socket descriptors
    session_set sess_set;
    unsigned int seed;

    getrandom(&seed, sizeof(seed), 0);
    srand(seed);

    memset(p_buffer, 0, BUFFER_SIZE);

    time_out.tv_sec = TIME_OUT;
    time_out.tv_usec = 0;

    // prepares client sockets
    prepare_sockets(p_client_socket_fds, &err);
    if (err) {
        fprintf(stderr, "Pointer to client sockets array is NULL.\n");
        return EXIT_FAILURE;
    }

    // initialize master socket
    init_master_socket(&fd_master_socket, &err);
    if (err) {
        print_socket_set_up_error();
        return EXIT_FAILURE;
    }
    
    set_up_master_socket(fd_master_socket, p_client_socket_fds, &err);
    if (err) {
        print_socket_set_up_error();
        close(fd_master_socket);
        return EXIT_FAILURE;
    }

    // type of socket created
    configure_address(&address, PORT);
    printf("Configured IP: %s, Port: %d\n", inet_ntoa(address.sin_addr), ntohs(address.sin_port));

    // bind the socket to localhost port 8080
    res = bind(fd_master_socket, (struct sockaddr *)&address, sizeof(address));
    if (res == FN_ERR) {
        print_bind_error_message();
        close(fd_master_socket);
        return EXIT_FAILURE;
    }
    printf("Binded master socket to port %d\n", PORT);

    // try to specify maximum of MAX_PENDING_CONNECTIONS pending connections for the master socket
    res = listen(fd_master_socket, MAX_PENDING_CONNECTIONS);
    if (res == FN_ERR) {
        print_listen_error_message();
        close(fd_master_socket);
        return EXIT_FAILURE;
    }
    printf("Listening on port %d\n", PORT);

    // accept the incoming connection
    addrlen = sizeof(address);

    signal(SIGINT, sigintHandler);
    
    session_set_init(&sess_set, &err);
    if (err) {
        fprintf(stderr, "Session set memory allocation failed.\n");
        close(fd_master_socket);
        return EXIT_FAILURE;
    }

    // main loop
    printf("Waiting for connections ...\n");
    while (running) {
        // clear the socket set
        FD_ZERO(&read_fds);
        // add master socket to set
        FD_SET(fd_master_socket, &read_fds);
        // add child sockets to set
        fd_max_val = add_active_sockets(p_client_socket_fds, &read_fds);
        if (fd_max_val == SOCKET_NOT_SET) {
            fd_max_val = fd_master_socket;
        }
        // reset timeout duration
        time_out.tv_sec = TIME_OUT;
        time_out.tv_usec = 0;

        // wait for an activity on one of the sockets
        res = select(fd_max_val + 1, &read_fds, NULL, NULL, &time_out);
        if (res == FN_ERR) {
            print_select_error_message();
            close(fd_master_socket);
            session_set_free(&sess_set, &err);
            return EXIT_FAILURE;
        }
        else if (res == 0) {
            printf("Timeout occurred.\n");
            continue;
        }
        else {
            printf("Activity detected.\n");
        }

        // new connection handling
        if (FD_ISSET(fd_master_socket, &read_fds)) {
            handle_new_connection(fd_master_socket, p_client_socket_fds, &address, addrlen, &sess_set, &err);
            if (err) {
                print_accept_error_message();
                break;
            }
        }

        // check for IO operations on other sockets
        for (i = 0; i < MAX_CLIENTS; i++) {
            fd_socket = p_client_socket_fds[i];

            if (fd_socket != SOCKET_NOT_SET && FD_ISSET(fd_socket, &read_fds)) {
                handle_client_io(fd_socket, p_client_socket_fds, p_buffer, i, &address, &addrlen, &sess_set, &err);
                if (err) {
                    print_read_error_message();
                    close(fd_socket);
                    p_client_socket_fds[i] = SOCKET_NOT_SET;
                    err = false;
                }
            }
        }

        printf("===\n");
    }
    // out of the main loop

    // close the sockets
    close(fd_master_socket);
    for (i = 0; i < MAX_CLIENTS; i++) {
        if (p_client_socket_fds[i] != SOCKET_NOT_SET) {
            close(p_client_socket_fds[i]);
        }
    }

    session_set_free(&sess_set, &err);
    if (err) {
        fprintf(stderr, "Session set free failed.\n");
    }

    return EXIT_SUCCESS;
}

#endif