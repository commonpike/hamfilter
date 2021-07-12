import imaplib,rfc822,string

# settings
host 	= 'YOURMAILHOST'	# required
port 	= None			# use None for default
user 	= 'YOURUSERNAME'	# required
password = 'YOURPASSWORD'	# required


# really move messages ?
testing = False

# delete original messages after copied ?
# nb: if you dont do this, and you run the filter twice,
# you will have duplicate messages in the destination folders
delete_originals = True;


# 2 maildirs are used as whitelist:
# maildir_me contains a few dummy messages sent TO me
maildir_me 		= "INBOX.hamfilter.config.me"

# maildir_friends contains a few dummy messages sent FROM friends
maildir_friends = "INBOX.hamfilter.config.friends"

# the input mailbox to filter
maildir_work 	= "INBOX"

# output mailboxes. leave empty for no action
maildir_fftf 	= "INBOX.hamfilter.from-friends.to-friends"
maildir_fftm 	= "INBOX.hamfilter.from-friends.to-me"
maildir_ffto 	= "INBOX.hamfilter.from-friends.to-others"
maildir_fmtf 	= "INBOX.hamfilter.from-me.to-friends"
maildir_fmtm 	= "INBOX.hamfilter.from-me.to-me"
maildir_fmto 	= "INBOX.hamfilter.from-me.to-others"
maildir_fotf 	= "INBOX.hamfilter.from-others.to-friends"
maildir_fotm 	= "INBOX.hamfilter.from-others.to-me"
maildir_foto 	= "INBOX.hamfilter.from-others.to-others"


# end config ----------------------------------------

class msg: # a file-like object for passing a string to rfc822.Message
	def __init__(self, text):
		self.lines = string.split(text, '\015\012')
		self.lines.reverse()
	def readline(self):
		try: return self.lines.pop() + '\n'
		except: return ''
				
def move(msgs,maildir):
	# if there is an exception .. the whole thing will die
	# that great. i won't catch exceptions.
	succes = True
	if maildir and len(msgs):
		msgsstr = ",".join(msgs)
		print "copying to %s : %s" % (maildir,msgsstr)
		if not testing:
			type,data = M.store(msgsstr, '-FLAGS', '\\Seen')
			#print '%s: %s' % (type,data)
			if type == 'OK':
				type,data = M.copy(msgsstr,maildir)
				#print '%s: %s' % (type,data)
				if type == 'OK':
					if delete_originals:
						type,data = M.store(msgsstr, '+FLAGS', '\\Deleted')
						#print '%s: %s' % (type,data)
						if type != 'OK': succes = False
				else: succes = False
			else: succes = False
				
	if not succes:
		print '%s: %s' % (type,data)		
	return succes
	
			

me	 	= [] # a list of emailadresses
friends = [] # a list of emailadresses
fftf 	= [] # a list of message numbers
fftm 	= []
ffto 	= []
fmtf 	= []
fmtm 	= []
fmto 	= []
fotf 	= []
fotm 	= []
foto 	= []
				
if port: M = imaplib.IMAP4(host,port)
else: M = imaplib.IMAP4(host)

print "* logging in ..."
M.login(user, password)

# find me
print "* reading config ..."

res = M.select(maildir_me)
if res[0]=='NO': raise RuntimeError('Could not select '+maildir_me)
	
typ, data = M.search(None, 'ALL')
for num in data[0].split():
	typ, data = M.fetch(num, "(BODY[HEADER.FIELDS (TO)])")
	res = rfc822.Message(msg(data[0][1]), 0)
	toaddr = res.getaddr('to')
	if toaddr[1] == "": recipient = toaddr[0]
	else: recipient = toaddr[1]
	if recipient: me.append(recipient.lower())
#print 'Me: %s ' % (me)
	
# find friends
res = M.select(maildir_friends)
if res[0]=='NO': raise RuntimeError('Could not select '+maildir_friends)
	
typ, data = M.search(None, 'ALL')
for num in data[0].split():
	typ, data = M.fetch(num, "(BODY[HEADER.FIELDS (FROM)])")
	res = rfc822.Message(msg(data[0][1]), 0)
	fromaddr = res.getaddr('from')
	if fromaddr[1] == "": sender = fromaddr[0]
	else: sender = fromaddr[1]
	if sender: friends.append(sender.lower())
#print 'Friends: %s ' % (friends)
	
#filter all mail

print "* reading mail ..."
res = M.select(maildir_work)
if res[0]=='NO': raise RuntimeError('Could not select '+maildir_work)


typ, data = M.search(None, 'ALL')
for num in data[0].split():
	
	typ, data = M.fetch(num, '(BODY[HEADER.FIELDS (FROM TO)])')
	res = rfc822.Message(msg(data[0][1]), 0)
	
	fromaddr = res.getaddr('from')
	if fromaddr[1] == "": sender = fromaddr[0]
	else: sender = fromaddr[1]
	if sender: sender = sender.lower()
	
	toaddr = res.getaddr('to')
	if toaddr[1] == "": recipient = toaddr[0]
	else: recipient = toaddr[1]
	if recipient: recipient = recipient.lower()
	
	print 'Message %s From: %s To: %s' % (num, sender, recipient)
	
	if sender:
		if me.count(sender):
			if me.count(recipient):
				fmtm.append(num)
			elif friends.count(recipient):
				fmtf.append(num)
			else:
				fmto.append(num)
				
		elif friends.count(sender):
			if me.count(recipient):
				fftm.append(num)
			elif friends.count(recipient):
				fftf.append(num)
			else:
				ffto.append(num)
				
		else:
			if me.count(recipient):
				fotm.append(num)
			elif friends.count(recipient):
				fotf.append(num)
			else:
				foto.append(num)

		
#action!
print "* filtering ..."	
succes = True
if succes: succes = move(fftf,maildir_fftf)
if succes: succes = move(fftm,maildir_fftm)
if succes: succes = move(ffto,maildir_ffto)

if succes: succes = move(fmtf,maildir_fmtf)
if succes: succes = move(fmtm,maildir_fmtm)
if succes: succes = move(fmto,maildir_fmto)

if succes: succes = move(fotf,maildir_fotf)
if succes: succes = move(fotm,maildir_fotm)
if succes: succes = move(foto,maildir_foto)
			
print "* logging out ..." 		
M.close() #expunges
M.logout()

print "* done."
