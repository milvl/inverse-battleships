OBJS = server.o err_messages.o session.o session_set.o
DEBUG_OBJS = server_debug.o err_messages_debug.o session_debug.o session_set_debug.o
SOURCE = server.c err_messages.h session.h session_set.h
OUT = server
DEBUG_OUT = server_debug
FLAGS = -Wall -c -pedantic -O3
DEBUG_FLAGS = -Wall -c -pedantic -g3
LFLAGS = 
CC = gcc

all: build clean-aux

build: $(OBJS)
	$(CC) $(OBJS) -o $(OUT) $(LFLAGS)

build_debug: $(DEBUG_OBJS)
	$(CC) $(DEBUG_OBJS) -o $(DEBUG_OUT) $(LFLAGS)

# server.o: $(SOURCE)
# 	$(CC) $(FLAGS) -o $@ $(SOURCE) 

# server_debug.o: $(SOURCE)
# 	$(CC) $(DEBUG_FLAGS) -o $@ $(SOURCE)

# generic rule for compiling .c files
%.o: %.c
	$(CC) $(FLAGS) -o $@ $<

%_debug.o: %.c
	$(CC) $(DEBUG_FLAGS) -o $@ $<

clean:
	rm -f $(OBJS) $(DEBUG_OBJS) $(OUT) $(DEBUG_OUT)

clean-aux:
	rm -f $(OBJS) $(DEBUG_OBJS)

valgrind: $(DEBUG_OUT)
	valgrind ./$(DEBUG_OUT)

valgrind_leakcheck: $(DEBUG_OUT)
	valgrind --leak-check=full ./$(DEBUG_OUT)

valgrind_extreme: $(DEBUG_OUT)
	valgrind --leak-check=full --show-leak-kinds=all --leak-resolution=high --track-origins=yes -s ./$(DEBUG_OUT)

valgrind_extreme_gdb: $(DEBUG_OUT)
	valgrind --leak-check=full --show-leak-kinds=all --leak-resolution=high --track-origins=yes --vgdb-error=0 -s ./$(DEBUG_OUT)
