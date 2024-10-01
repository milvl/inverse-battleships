#include <stdio.h>
#include <string.h>
#include <sys/socket.h>
#include <netinet/in.h>

#define EXIT_FAILURE 1
#define EXIT_SUCCESS 0
#define INF_LOOP 1
#define SOCK_INVALID -1
#define PROTOCOL_AUTO_CHOICE 0
#define SERVER_ADDRESS "127.0.0.1"
#define SERVER_PORT 8888
#define CALC_SERVER_PORT 2000
#define VALIDATOR_SERVER_PORT 2001
#define REVERSE_SERVER_PORT 2002
#define BYTES_USER_INPUT_BUFFER_SIZE 1000
#define BYTES_SERVER_REPLY_BUFFER 2000
#define RETURN_FAIL -1
#define NO_FLAGS 0

/**
 * @brief 
 * 
 * @param argc 
 * @param argv 
 * @return int 
 */
int main(int argc , char *argv[]) {
    int res;
    int fd_sock;
    struct sockaddr_in remote_addr;
    char p_input_buff[BYTES_USER_INPUT_BUFFER_SIZE];
    char p_server_reply_buff[BYTES_SERVER_REPLY_BUFFER];

    memset(p_input_buff, 0, sizeof(p_input_buff));
    memset(p_server_reply_buff, 0, sizeof(p_server_reply_buff));

    // create a socket
    fd_sock = socket(AF_INET , SOCK_STREAM , PROTOCOL_AUTO_CHOICE);
    if (fd_sock == SOCK_INVALID) {
        printf("Could not create socket");
        return EXIT_FAILURE;
    }
    // puts("Socket created");
    printf("Socket created\n");

    remote_addr.sin_addr.s_addr = inet_addr(SERVER_ADDRESS);
    remote_addr.sin_family = AF_INET;
    remote_addr.sin_port = htons(SERVER_PORT);

    // try to connect to remote server
    res = connect(fd_sock , (struct sockaddr *)&remote_addr , sizeof(remote_addr));
    if (res == RETURN_FAIL) {
        perror("connect failed. Error");
        close(fd_sock);
        return EXIT_FAILURE;
    }

    // puts("Connected\n");
    printf("Connected\n\n");

    // keep communicating with server
    while(INF_LOOP) {
        printf("Enter message : ");
        fgets(p_input_buff, sizeof(p_input_buff), stdin);
        // remove newline if present
        p_input_buff[strcspn(p_input_buff, "\n")] = 0;

        // send some data
        res = send(fd_sock, p_input_buff, strlen(p_input_buff), NO_FLAGS);  // res <- err flag or number of bytes sent
        if (res == RETURN_FAIL) {
            // puts("Send failed");
            printf("Send failed\n");
            break;
        }

        // receive a reply from the server
        res = recv(fd_sock , p_server_reply_buff, sizeof(p_server_reply_buff), NO_FLAGS);   // res <- err flag or number of bytes received
        if (res == RETURN_FAIL) {
            // puts("recv failed");
            printf("recv failed\n");
            break;
        }
        // no data recieved
        else if (res == 0) {
            printf("Connection closed by server\n");
            break;
        }

        // ensure null termination
        p_server_reply_buff[sizeof(BYTES_SERVER_REPLY_BUFFER) - 1] = '\0';

        // puts("Server reply :");
        // puts(p_server_reply_buff);
        printf("Server reply :\n");
        printf("%s", p_server_reply_buff);
        printf("\n");

        // clear the buffers because why not
        memset(p_input_buff, 0, sizeof(p_input_buff));
        memset(p_server_reply_buff, 0, sizeof(p_server_reply_buff));
    }

    close(fd_sock);
    return EXIT_SUCCESS;
}