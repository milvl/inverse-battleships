#include <stdio.h>
#include <string.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <sys/types.h>
#include <sys/un.h>
#include <unistd.h>
#include <stdlib.h>
#include <stdbool.h>

#define EXIT_FAILURE 1
#define EXIT_SUCCESS 0
#define INF_LOOP 1
#define SOCK_INVALID -1
#define PROTOCOL_AUTO_CHOICE 0
#define SERVER_ADDRESS "147.228.67.67"
#define CALC_SERVER_PORT 2000
#define ECHO_SERVER_PORT 2001
#define REVERSE_SERVER_PORT 2002
#define BYTES_USER_INPUT_BUFFER_SIZE 1000
#define BYTES_SERVER_REPLY_BUFFER 2000
#define RETURN_FAIL -1
#define RETURN_OK 0
#define BREAK_LOOP 1
#define NO_FLAGS 0

/**
 * @brief Sends a message and receives server reply. 
 * 
 * @param fd_sock File descriptor of the socket
 * @param p_message_buff Pointer to the buffer with the message to send
 * @param message_buff_size Maximum size allocated for the message buffer
 * @param p_server_reply_buff Pointer to the buffer with the reply destination
 * @param server_reply_buff_size Maximum size allocated for the reply buffer
 * @param p_err Pointer to the variable with error flag
 */
void send_and_receive(int fd_sock, char *p_message_buff, size_t message_buff_size, char *p_server_reply_buff, size_t server_reply_buff_size, int *p_err) {
    int message_size = strlen(p_message_buff);

    if (message_size >= message_buff_size) {
        printf("Input too long for buffer.\n");
        *p_err = RETURN_FAIL;
        return;
    }
    
    // send some data
    *p_err = send(fd_sock, p_message_buff, strlen(p_message_buff), NO_FLAGS);  // res <- err flag or number of bytes sent
    if (*p_err == RETURN_FAIL) {
        printf("Send failed\n");
        return;
    }
    printf("Sent: %s", p_message_buff);

    // receive a reply from the server
    *p_err = recv(fd_sock, p_server_reply_buff, server_reply_buff_size, NO_FLAGS);   // res <- err flag or number of bytes received
    if (*p_err == RETURN_FAIL) {
        printf("recv failed\n");
        return;
    }
    // no data recieved
    else if (*p_err == 0) {
        printf("Connection closed by server\n");
        return;
    }

    // ensure null termination
    p_server_reply_buff[server_reply_buff_size - 1] = '\0';
    
    *p_err = RETURN_OK;
    return;
}

/**
 * @brief Handles interaction with the calculator server.
 * 
 * @param fd_sock Socket file descriptor
 * @param p_input_buff Pointer to user input buffer
 * @param input_buff_size User input buffer max size
 * @param p_server_reply_buff Pointer to server reply buffer
 * @param server_reply_buff_size Server reply buffer max size
 */
void handle_calc_server(int fd_sock, char *p_input_buff, size_t input_buff_size, char *p_server_reply_buff, size_t server_reply_buff_size) {
    char *init_message_end = "Operation: [\"plus\", \"minus\", \"division\", \"multiply\"]\n";
    bool passed_init_messages = false;
    int res, err;
    int ascii_offset = 42;
    unsigned long long operand1, operand2;
    char operator;
    char *str_operators[] = {"multiply", "plus", "_", "minus", "_", "division"};
    
    // ignore first two replies - acceptable for this basic client
    while (!passed_init_messages) {
        // receive a reply from the server
        res = recv(fd_sock, p_server_reply_buff, server_reply_buff_size, NO_FLAGS);   // res <- err flag or number of bytes received
        if (res == RETURN_FAIL) {
            printf("recv failed\n");
            return;
        }
        // no data recieved
        else if (res == 0) {
            printf("Connection closed by server\n");
            return;
        }

        if (strstr(p_server_reply_buff, init_message_end)) {
            passed_init_messages = true;
        }

        // clear the reply buffer
        memset(p_server_reply_buff, 0, server_reply_buff_size);
    }

    printf("\nEnter <operand><operator><operand>\nAvailible operators: +, -, /, *\n\n");
    fgets(p_input_buff, input_buff_size, stdin);

    // parse the input to extract operands and operator
    if (sscanf(p_input_buff, "%llu %c %llu", &operand1, &operator, &operand2) != 3) {
        printf("Invalid input format. Next time, enter: <operand> <operator> <operand>\n");
        return;
    }

    // check for valid operator
    if (operator != '+' && operator != '-' && operator != '*' && operator != '/') {
        printf("Invalid operator. Next time, please use one of the following: +, -, *, /\n");
        return;
    }

    // check for valid operands
    if (operand1 < 0L || operand2 < 0L) {
        printf("Negative operands are not allowed. Next time, use possitive values.\n");
        return;
    }

    // edge case check
    if (operator == '/' && operand2 == 0L) {
        printf("Division by zero is not defined.\n");
        return;
    }

    sprintf(p_input_buff, "%s|%llu|%llu\n", str_operators[(int) operator - ascii_offset], operand1, operand2);
    
    send_and_receive(fd_sock, p_input_buff, input_buff_size, p_server_reply_buff, server_reply_buff_size, &err);
    if (err) {
        return;
    }

    printf("Server reply:\n%s\n", p_server_reply_buff);
}

/**
 * @brief Handles interaction with the echo server.
 * 
 * @param fd_sock Socket file descriptor
 * @param p_input_buff Pointer to user input buffer
 * @param input_buff_size User input buffer max size
 * @param p_server_reply_buff Pointer to server reply buffer
 * @param server_reply_buff_size Server reply buffer max size
 */
void handle_echo_server(int fd_sock, char *p_input_buff, size_t input_buff_size, char *p_server_reply_buff, size_t server_reply_buff_size) {
    int err;

    printf("Enter message (enter to break): ");
    fgets(p_input_buff, input_buff_size, stdin);
    // ensure memory integrity
    p_input_buff[input_buff_size - 1] = '\0';

    if (p_input_buff[0] == '\n') {
        printf("End requested.\n");
        return;
    }
    
    printf("Inputed: %s", p_input_buff);

    send_and_receive(fd_sock, p_input_buff, input_buff_size, p_server_reply_buff, server_reply_buff_size, &err);
    if (err) {
        return;
    }

    printf("Server reply: %s\n", p_server_reply_buff);

    if (strcmp(p_input_buff, p_server_reply_buff)) {
        printf("Validation failed, the reply is NOT the same as the input\n");
    }
    else {
        printf("Validation passed, the reply is the same as the input.\n");
    }

    // clear the buffers because why not
    memset(p_input_buff, 0, input_buff_size);
    memset(p_server_reply_buff, 0, server_reply_buff_size);
}

/**
 * @brief Handles interaction with the reverse string validation server.
 * 
 * @param fd_sock Socket file descriptor
 * @param p_input_buff Pointer to user input buffer
 * @param input_buff_size User input buffer max size
 * @param p_server_reply_buff Pointer to server reply buffer
 * @param server_reply_buff_size Server reply buffer max size
 */
void handle_reverse_server(int fd_sock, char *p_input_buff, size_t input_buff_size, char *p_server_reply_buff, size_t server_reply_buff_size) {
    int i = 0;
    int res, err;
    const char *p_reply_end, *p_tmp;

    // receive a reply from the server
    res = recv(fd_sock, p_server_reply_buff, server_reply_buff_size, NO_FLAGS);   // res <- err flag or number of bytes received
    if (res == RETURN_FAIL) {
        printf("recv failed\n");
        return;
    }
    // no data recieved
    else if (res == 0) {
        printf("Connection closed by server\n");
        return;
    }

    printf("Received: %s", p_server_reply_buff);

    // reverse message
    p_reply_end = strstr(p_server_reply_buff, "\n");
    // sanity check
    if (p_reply_end - p_server_reply_buff >= strlen(p_server_reply_buff)) {
        printf("Logical pointer error\n");
    }
    p_tmp = p_reply_end - 1;
    while (i < strlen(p_server_reply_buff)) {
        p_input_buff[i] = *p_tmp;
        p_tmp--;
        i++;
    }
    p_input_buff[strlen(p_server_reply_buff) - 1] = '\n';

    // printf("Reversed: %s", p_input_buff);
    
    // clear reply buffer
    memset(p_server_reply_buff, 0, server_reply_buff_size);

    send_and_receive(fd_sock, p_input_buff, input_buff_size, p_server_reply_buff, server_reply_buff_size, &err);
    if (err) {
        return;
    }

    printf("Server reply: %s", p_server_reply_buff);
}

/**
 * @brief Main function.
 * 
 * @return int 0 if OK, anything elso on failure/error
 */
int main() {
    int res;
    int fd_sock;
    int port;
    int is_choice_invalid = 1;
    void (*handle_server)(int, char*, size_t, char*, size_t);
    struct sockaddr_in remote_addr;
    char p_input_buff[BYTES_USER_INPUT_BUFFER_SIZE];
    char p_server_reply_buff[BYTES_SERVER_REPLY_BUFFER];

    memset(p_input_buff, 0, sizeof(p_input_buff));
    memset(p_server_reply_buff, 0, sizeof(p_server_reply_buff));

    while (p_input_buff[0] == '\0' || p_input_buff[0] == '\n') {
        printf("Choose server:\n 1 - calculator\n 2 - echo server\n 3 - reverse server\n\n");
        fgets(p_input_buff, 3, stdin);
    }

    if (!strcmp("1\n", p_input_buff)) {
        port = CALC_SERVER_PORT;
        is_choice_invalid = 0;
        handle_server = handle_calc_server;
    } else if (!strcmp("2\n", p_input_buff)) {
        port = ECHO_SERVER_PORT;
        is_choice_invalid = 0;
        handle_server = handle_echo_server;
    } else if (!strcmp("3\n", p_input_buff)) {
        port = REVERSE_SERVER_PORT;
        is_choice_invalid = 0;
        handle_server = handle_reverse_server;
    }
    if (is_choice_invalid) {
        printf("Invalid choice. Terminating.\n");
        return EXIT_FAILURE;
    }

    memset(p_input_buff, 0, sizeof(p_input_buff));

    printf("Server ipv4 address: %s\n", SERVER_ADDRESS);
    printf("Chosen port: %d\n", port);

    // create a socket
    fd_sock = socket(AF_INET, SOCK_STREAM, PROTOCOL_AUTO_CHOICE);
    if (fd_sock == SOCK_INVALID) {
        printf("Could not create socket");
        return EXIT_FAILURE;
    }
    else {
        printf("Socket created\n");
    }

    // prepare sockaddr struct
    memset(&remote_addr, 0, sizeof(struct sockaddr_in));
    remote_addr.sin_addr.s_addr = inet_addr(SERVER_ADDRESS);
    remote_addr.sin_family = AF_INET;
    remote_addr.sin_port = htons(port);

    // try to connect to remote server
    res = connect(fd_sock, (struct sockaddr *)&remote_addr, sizeof(remote_addr));
    if (res == RETURN_FAIL) {
        perror("Connect failed. Error.\n");
        close(fd_sock);
        return EXIT_FAILURE;
    }
    else {
        printf("Connected\n");
    }

    // communicating with server
    handle_server(fd_sock, p_input_buff, sizeof(p_input_buff), p_server_reply_buff, sizeof(p_server_reply_buff));
    close(fd_sock);

    return EXIT_SUCCESS;
}