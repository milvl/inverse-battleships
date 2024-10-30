import java.io.IOException;
import java.io.ObjectInputStream;
import java.io.ObjectOutputStream;
import java.io.*;
import java.lang.ClassNotFoundException;
import java.lang.Runnable;
import java.lang.Thread;
import java.net.ServerSocket;
import java.net.Socket;
import java.net.InetAddress;
import java.net.*;

//-Djava.net.preferIPv4Stack=true
 
public class serverTCPSingle
{
	public static void main(String[] args )
	{
		System.out.print( "Server TCP\n" );

            	try {
    			ServerSocket server = new ServerSocket( 10001, 10, InetAddress.getByName("rattmann.kennny.cz") );

			while (true) 
			{
                		Socket socket = server.accept();
				InetAddress adresa = socket.getInetAddress();
				System.out.print("Pripojil se klient z: "+adresa.getHostAddress()+"/"+adresa.getHostName()+"\n" );

				InputStreamReader isr = new InputStreamReader(socket.getInputStream());
				BufferedReader br = new BufferedReader(isr);

				OutputStreamWriter osw = new OutputStreamWriter(socket.getOutputStream());
				PrintWriter pw = new PrintWriter(osw);


			        String message = br.readLine();
				System.out.println("Message Received: " + message);
				
				//Thread.currentThread().sleep(5000);

            			pw.println("Hallo");
				pw.flush();
            			socket.close();
			}
            	} 
		catch (Exception e) 
		{
                	e.printStackTrace();
            	}
        }
}
