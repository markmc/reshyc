
all: function.zip

function.zip: function.py
	zip -r function.zip function.py

function.py: function.in.py transforms.in.py require_ftp_details
	@echo "Substituting FTP_DIR, FTP_SERVER, FTP_USER, and FTP_PASSWORD into function.py"
	@sed 's|@@FTP_DIR@@|$(FTP_DIR)|; s|@@FTP_SERVER@@|$(FTP_SERVER)|; s|@@FTP_USER@@|$(FTP_USER)|; s|@@FTP_PASSWORD@@|$(FTP_PASSWORD)|' < function.in.py > function.py
	cat transforms.in.py >> function.py

clean:
	rm -f function.py function.zip


require_ftp_details:
ifndef FTP_DIR
        $(error FTP_DIR is not defined)
endif
ifndef FTP_SERVER
        $(error FTP_SERVER is not defined)
endif
ifndef FTP_USER
        $(error FTP_USER is not defined)
endif
ifndef FTP_PASSWORD
        $(error FTP_PASSWORD is not defined)
endif
