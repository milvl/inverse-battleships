#ifndef __SESSION_H
#define __SESSION_H

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>

#define SESSION_STATE_CONNECTED 1
#define SESSION_STATE_AUTHORIZED 2

typedef struct {
    int fd_sock;
    int state;
    int num;
} session;

/**
 * @brief Initializes the session.
 * 
 * @param p_session Pointer to the session
 * @param fd_sock Socket file descriptor
 * @param num Session number
 * @param p_err Pointer to the error flag
 */
void init_session(session *p_session, int fd_sock, int num, int *p_err);

/**
 * @brief Authenticates the session.
 * 
 * @param p_session Pointer to the session
 * @param p_buffer Pointer to the buffer
 * @param buffer_size Buffer size
 * @param p_err Pointer to the error flag
 * @return int 0 if OK, anything else on failure
 */
bool session_authenticate(session *p_session, char *p_buffer, int buffer_size, int *p_err);

/**
 * @brief Validates the session.
 * 
 * @param p_session Pointer to the session
 * @param p_buffer Pointer to the buffer
 * @param buffer_size Buffer size
 * @param p_err Pointer to the error flag
 * @return int 0 if OK, anything else on failure
 */
bool session_validate(session *p_session, char *p_buffer, int buffer_size, int *p_err);

#endif