#include "session.h"

void init_session(session *p_session, int fd_sock, int num, int *p_err) {
    if (p_session == NULL) {
        *p_err = true;
        return;
    }

    p_session->fd_sock = fd_sock;
    p_session->state = SESSION_STATE_CONNECTED;
    p_session->num = num;
}

bool session_authenticate(session *p_session, char *p_buffer, int buffer_size, int *p_err) {
    // sanity check
    if (p_session == NULL) {
        *p_err = true;
        return false;
    }

    // authenticate
    if (p_session->state == SESSION_STATE_CONNECTED) {
        if (strcmp("HELLO\n", p_buffer) == 0) {
            p_session->state = SESSION_STATE_AUTHORIZED;
            return true;
        }
        else {
            return false;
        }
    }
    else {
        return true;
    }
}

bool session_validate(session *p_session, char *p_buffer, int buffer_size, int *p_err) {
    long num;
    char *endptr;
    
    // sanity check
    if (p_session == NULL) {
        *p_err = true;
        return false;
    }

    // read the number
    num = strtol(p_buffer, &endptr, 10);
    if (endptr == p_buffer || *endptr != '\n') {
        return false;
    }

    // validate
    if (p_session->state != SESSION_STATE_AUTHORIZED) {
        return false;
    }
    if (num == (long)(p_session->num * 2)) {
        return true;
    }
    
    return false;
}