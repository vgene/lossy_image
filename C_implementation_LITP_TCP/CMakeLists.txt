cmake_minimum_required(VERSION 3.13)
project(COS561 C CXX)

set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 11)


include_directories(.)

add_executable(LITP_test
        LITP.h
        test_litp.c
        )

add_executable(UDPClient
        LITP.h
        UDPClient.c
        )

add_executable(UDPServer
        LITP.h
        UDPServer.c
        )

add_executable(TCPServer
        TCPServer.cpp
        )

add_executable(TCPClient
        TCPClient.cpp
        )
