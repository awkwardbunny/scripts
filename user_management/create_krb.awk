BEGIN {
	#print "BEGIN"
	FS=":"
	print "#!/bin/bash"
	print "echo \"#### AUTOMATICALLY GENERATED ####\" > passwords"
}

NR!=1 { 
	"pwgen -cns1B 10 100000" | getline pass
	print "kadmin.local -q \"addprinc -pw "pass" "$1"\""
	print "echo "$1,pass" >> passwords"
	print "sed 's/$username/"$1"/g; s/$password/"pass"/g' /root/.bin/creation_mail.template | sendmail "$1"@cooper.edu"
}

END {
	#print "END"
}
