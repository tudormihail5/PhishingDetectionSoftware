# Phishing Detection Software

### What it does:

The significance of this software derives from its comprehensive approach to phishing detection, which combines four distinct methods to tackle different aspects of a website: file downloads, the technical part, its text, and its reputation. This multi-faceted strategy is intended to enhance the accuracy of phishing detection and reduce the incidence of false positives and negatives, making the internet a safer place for everyone. 

The user can paste an URL inside the text input, click the 'Website in English' checkbox if the website is in English, then click the 'Check URL' button and wait for the results. Clicking the 'History' button from the top left-hand corner will take the user to the 'History' page of the website, which displays all the URLs tested by the users, together with their corresponding results. If the user wants to find a particular URL, they can type a part of it inside the text bar, and click 'Search'. Under the history table there is the translation of the history abbreviations. Clicking the 'Help' button from the opposite top corner will take the user to a comprehensive help page.

### How I built it:

- I used JavaFX to create the GUI.
- I created every functionality of the GUI in MainController, including the automatic refresh of the app (every 5 seconds), users being able to communicate in real time.
- MainController is also sending the requests to the server, using sockets.
- The Main class starts the application, loading Main.fxml, setting the size of the GUI, and displaying it.
- JabberMessage eases the communication between the server and the client, and is used by MainController to send the messages, but also by ClientConnection.
- ClientConnection receives the messages from the client, and completes the task, using the settled protocol.
- JabberDatabase deals with the database, adding things to it, or reading information requested by the server.
- JabberServer runs the server, delivering a 'Waiting' (for a client) message after compiling.

### Challenges I ran into:
