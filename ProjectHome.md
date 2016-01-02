**A positive approach to wanted email**

Identifying spam is complex. Identifying ham is easy.

hamfilter.py moves all the messages from one imap mailfolder  into other specified folders, based on the sender and recipients. I have this script in a cronjob, nightly, so I wake up with an empty inbox every day.

'known senders' are called 'friends' and 'known recipients' are called 'me'. To find out what addresses are friends, it looks at the sender of all messages in one specific imap folder. To find which adresses are 'me', it looks at all recipients in another specific imap folder.

Next, it parses the work folder and for each message, decides wether its from a friend and/or to me, and moves the messages to one of the designated imap folders for messages
  * from friends
    * to friends
    * to me
    * to others
  * from me
    * to friends
    * to me
    * to others
  * from others
    * to friends
    * to me
    * to others

Obviously, some or all of these mailboxes can be the same. Configure your setup by editing the script.

# WARNING #

This script remotely moves stuff around in your mailbox. It deletes messages while doing so. If it fails halfway it may leave you with a broken or messed up mailbox. Use it with great care.  **I take NO responsibilty for use or abuse of this script**. Test it first. Read this line twice.