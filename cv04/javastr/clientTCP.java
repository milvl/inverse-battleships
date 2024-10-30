import java.io.*;
import java.net.*;

class clientTCP
{
	public static void main(String argv[]) throws Exception
	{
		String sentence;
		String modifiedSentence;
		Socket socket = new Socket("rattmann.kennny.cz", 10001);
		InetAddress adresa = socket.getInetAddress();
		System.out.print("Pripojuju se na : "+adresa.getHostAddress()+" se jmenem : "+adresa.getHostName()+"\n" );

		InputStreamReader isr = new InputStreamReader(socket.getInputStream());
		BufferedReader br = new BufferedReader(isr);

		OutputStreamWriter osw = new OutputStreamWriter(socket.getOutputStream());
		PrintWriter pw = new PrintWriter(osw);

		pw.println("HalloXXXX");
		pw.flush();

		String message = br.readLine();

		System.out.println("Message Received: " + message);
		socket.close();
	}
}
