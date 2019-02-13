BEGIN {
	#print "BEGIN"
	FS=":"
	uid = 5000
	home = "/afs/ee.cooper.edu/user"
	public = "/afs/ee.cooper.edu/public/www"
}

NR==1 {
	uid = $1
	#print "Start UID from " uid
}

NR!=1 { 
	fl = substr($1,1,1)
	# Create AFS user
	print ("pts createuser",$1,uid++)
	# Create user volume
	print ("vos create stallman a user."$1,"0")
	print ("fs mkm",home"/"fl"/"$1,"user."$1,"-rw")
	print ("fs sa",home"/"fl"/"$1,$1,"all")
	# Create public volume
	print ("vos create stallman a public."$1,"0")
	print ("fs mkm",public"/"fl"/"$1,"public."$1,"-rw")
	print ("fs sa",public"/"fl"/"$1,$1,"all")
	print ("fs sa",public"/"fl"/"$1,"system:anyuser rl")
	print ("ln -s",public"/"fl"/"$1, home"/"fl"/"$1"/public_html")
	print ("")
}

END {
	#print "END"
}
