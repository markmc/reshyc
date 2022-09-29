
all: function.zip

function.zip: function.py
	zip -r function.zip function.py

function.py: function.in.py require_ftp_details
	@echo "Substituting FTP_USER, FTP_PASSWORD, and FTP_SERVER_ROLE into function.py"
	@sed 's|@@FTP_USER@@|$(FTP_USER)|; s|@@FTP_PASSWORD@@|$(FTP_PASSWORD)|; s|@@FTP_SERVER_ROLE@@|$(FTP_SERVER_ROLE)|' < function.in.py > function.py

clean:
	rm -f function.py function.zip


require_ftp_details:
ifndef FTP_SERVER_ROLE
        $(error FTP_SERVER_ROLE is not defined)
endif
ifndef FTP_USER
        $(error FTP_USER is not defined)
endif
ifndef FTP_PASSWORD
        $(error FTP_PASSWORD is not defined)
endif
