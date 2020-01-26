package com.sahara;

import android.util.Log;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.io.PrintWriter;
import java.net.Socket;

 class Communicate
{

    public static String SERVER_IP;
    public static int SERVER_PORT;
    public static OutputStream output;
    public static BufferedReader input;
    public static String message;
    public static String connectionStatus;
    public static String msgReceivedStatus;

    public Communicate(String serverIP, int serverPort)
    {
        SERVER_IP = serverIP;
        SERVER_PORT = serverPort;

        connectionStatus = "NO_CONNECTION";
        msgReceivedStatus = "NO_MSG";

        Thread createSocket = new CreateSocketThread();
        createSocket.start();
    }

    public String getMessage() {
        while(true)
        {
            if (msgReceivedStatus.equals("RECEIVED"))
                break;
        }
        msgReceivedStatus = "NO_MSG";
        return message;
    }


    class CreateSocketThread extends Thread
    {
        public void run()
        {
            Socket socket;
            while(true)
            {
                try
                {
                    socket = new Socket(SERVER_IP, SERVER_PORT);
                    socket.setSendBufferSize(4096);

                    output = socket.getOutputStream();//new PrintWriter(socket.getOutputStream());
                    input = new BufferedReader(new InputStreamReader(socket.getInputStream()));

                    connectionStatus = "SUCCESS";
                    new ReceiveData().start();

                    break;
                }
                catch (IOException e)
                {
                    connectionStatus = "FAILED";
                    e.printStackTrace();
                }
            }

        }
    }

    /*-------------------------------------------------------------------------------------------------------------------------*/

    class ReceiveData extends Thread
    {
        @Override
        public void run()
        {
            while(true)
            {
                try
                {
                    String msg = input.readLine();

                    if (msg != null)
                    {
                        message = msg;
                        msgReceivedStatus = "RECEIVED";
                    }
                }
                catch (IOException e)
                {
                    e.printStackTrace();
                }
            }

        }
    }



    /*-------------------------------------------------------------------------------------------------------------------------*/

    static class SendData extends Thread
    {
        private byte[] data;


        SendData(byte[] data)
        {
            this.data = data;
        }

        @Override
        public void run()
        {
            if (connectionStatus.equals("SUCCESS"))
            {
                try {
                    output.write(data );
                    output.write("eof".getBytes());
                    output.flush();
                } catch (IOException e) {
                    e.printStackTrace();
                }

            }
        }

    }

    /*-------------------------------------------------------------------------------------------------------------------------*/
}

