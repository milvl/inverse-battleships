#ifndef __SESSION_SET_H
#define __SESSION_SET_H

#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>
#include <errno.h>
#include "session.h"
#include "const.h"

typedef struct {
    void *p_array;
    unsigned int elem_size;
    int top;
    int size;
} session_set;

/**
 * @brief Initializes the session set.
 * 
 * @param p_array Pointer to the session set
 * @param p_err Pointer to the error flag
 */
void session_set_init(session_set *p_sess_set, int *p_err);

/**
 * @brief Pushes a session to the session set.
 * 
 * @param p_sess_set Pointer to the session set
 * @param p_session Pointer to the session
 * @param p_err Pointer to the error flag
 */
void session_set_add(session_set *p_sess_set, session *p_session, int *p_err);

/**
 * @brief Checks if the session set contains a session.
 * 
 * @param p_sess_set Pointer to the session set
 * @param fd File descriptor
 * @param p_err Pointer to the error flag
 * @return true if the session set contains the session, false otherwise
 */
bool session_set_contains(session_set *p_sess_set, int fd, int *p_err);

/**
 * @brief Removes a session from the session set.
 * 
 * @param p_sess_set Pointer to the session set
 * @param fd File descriptor
 * @param p_err Pointer to the error flag
 */
void session_set_remove(session_set *p_sess_set, int fd, int *p_err);

/**
 * @brief Gets a session from the session set.
 * 
 * @param p_sess_set Pointer to the session set
 * @param fd File descriptor
 * @param p_err Pointer to the error flag
 * @return session* Pointer to the session
 */
session *session_set_peek(session_set *p_sess_set, int fd, int *p_err);

/**
 * @brief Frees the session set.
 * 
 * @param p_sess_set Pointer to the session set
 * @param p_err Pointer to the error flag
 */
void session_set_free(session_set *p_sess_set, int *p_err);



#endif