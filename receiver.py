import subprocess
import urllib2,os,csv,urllib

def database_lookup(email_ID):
	file_path="local_database/"	
	unity_ID=email_ID.split("@")[0]
	#print unity_ID
	file_path+=unity_ID+".pem"
	flag=0
	if os.path.exists(file_path):
		flag=1
		print "Sender key found in local database!"
	else:
		print "Looking up web database"
		read_object=urllib2.urlopen("https://courses.ncsu.edu/csc574/lec/001/CertificateRepo")
		csv_file=csv.reader(read_object)
		for i in csv_file:
			#print i[0]
			if i[0]==unity_ID:
				receiver_certificate=urllib.URLopener()
				receiver_certificate.retrieve(i[1],file_path)
				flag=1
	if flag==0:
		print "Could not find sender key!"
		exit()
	return

def main():
#read the email	
	fo1=open("received_mail.txt","r+")
	email=fo1.read()
	fo1.close()
	#print email	
	rcv_id=email.split("----BEGIN CSC574 MESSAGE----")[0].split(",to: ")[1]
	sender_id=email.split("----BEGIN CSC574 MESSAGE----")[0].split(",to: ")[0].split(": ")[1]
	print "Message from: " + sender_id
	print "Message to: " + rcv_id
	sender_key=sender_id.split("@")[0] + ".pem"
	receiver_key=rcv_id.split("@")[0] + ".pem"
	#print sender_key

#sender's key lookup
	database_lookup(sender_id)

#Verify sender's certificate with CA
	p=subprocess.Popen(["openssl","verify","-CAfile","root-ca.crt",sender_key],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
	(output,error)=p.communicate()
	if "error 20" in error:
		print "Cannot verify sender!"
	else:
		print "Sender verified!"
	
	email_split=email.split("\n")
	#print email_split
	email_contents="\n".join([email_split[i] for i in range(2,5)]) #to compare hash of the message content originally hashed
	#print email_contents
	
	fo2=open("encrypted_email.txt","w+")
	fo2.write(email_contents)
	fo2.close()
	
	email_hash=subprocess.check_output(["openssl","dgst","-sha1","encrypted_email.txt"])
	#print email_hash
	#print email_hash.split(" ")[1]

#verifying signature in the message with the received email's signature
	signature=email_split[6]
	#print signature
	fo3=open("signature.txt","w+")
	fo3.write(signature)
	fo3.close()
	
	check=subprocess.check_output(["openssl","rsautl","-inkey","public_key.pem","-pubin","-in","signature.txt"])

	#print check
	if check!=email_hash.split(" ")[1]:
		print "Signature doesn't match!"
		exit()

	fo4=open("session_key_from_email.txt","w+")
	fo4.write(email_split[2])
	fo4.close()
	#print email_split[2]
		
	session_key_retrieved=subprocess.check_output(["openssl","rsautl","-decrypt","-in","session_key_from_email.txt","-inkey","private_key.pem"])
	#print session_key_retrieved

	fo4=open("message_from_email.txt","w+")
	fo4.write(email_split[4])
	fo4.close()

	message_retrieved=subprocess.check_output(["openssl","enc","-d","-aes-256-cbc","-base64","-A","-in","message_from_email.txt","-k",session_key_retrieved])
	print ("The message is:"+message_retrieved)

if __name__=="__main__":
	main()
