OBJS = client.o
DEBUG_OBJS = client_debug.o
SOURCE = client.c
OUT = client
DEBUG_OUT = client_debug
FLAGS = -Wall -c -pedantic -O3
DEBUG_FLAGS = -Wall -c -pedantic -g3
LFLAGS = 
CC = gcc

all: build

build: $(OBJS)
	$(CC) $(OBJS) -o $(OUT) $(LFLAGS)

build_debug: $(DEBUG_OBJS)
	$(CC) $(DEBUG_OBJS) -o $(DEBUG_OUT) $(LFLAGS)

client.o: $(SOURCE)
	$(CC) $(FLAGS) -o $@ $(SOURCE) 

client_debug.o: $(SOURCE)
	$(CC) $(DEBUG_FLAGS) -o $@ $(SOURCE)

clean:
	rm -f $(OBJS) $(DEBUG_OBJS) $(OUT) $(DEBUG_OUT)

valgrind: $(DEBUG_OUT)
	valgrind ./$(DEBUG_OUT)

valgrind_leakcheck: $(DEBUG_OUT)
	valgrind --leak-check=full ./$(DEBUG_OUT)

valgrind_extreme: $(DEBUG_OUT)
	valgrind --leak-check=full --show-leak-kinds=all --leak-resolution=high --track-origins=yes --vgdb-error=0 ./$(DEBUG_OUT)
