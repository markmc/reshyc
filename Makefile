
all: sailwave

sailwave:
	wine '/home/markmc/.wine/drive_c/Program Files (x86)/Sailwave/sailwave.exe'

sw2_29_0.exe:
	curl -O https://www.sailwave.com/download/sailwave/sw2_29_0.exe

install: sw2_29_0.exe
	wine ./sw2_29_0.exe

clean:
	rm -f sw2_29_0.exe

wineclean:
	rm -rf ~/.wine

require_password:
ifndef FTP_SERVER
	$(error FTP_SERVER is not defined)
endif
ifndef FTP_USER
	$(error FTP_USER is not defined)
endif
ifndef FTP_PASSWORD
	$(error FTP_PASSWORD is not defined)
endif

backup: require_password
	@wget -m ftp://$(FTP_USER):$(FTP_PASSWORD)@$(FTP_SERVER)/reshyc

AL_OFFSHORE_FILES := 2022_AL_class1.htm 2022_AL_class2.htm 2022_AL_class4.htm 2022_AL_class5.htm
AL_INSHORE_FILES := 2022_AL_class3.htm 2022_AL_h17.htm 2022_AL_pup.htm 2022_AL_squib.htm

$(AL_OFFSHORE_FILES): 2022-autumn-league-offshore.json 2022_AL_offshore.htm scripts/chunk.py
	python scripts/chunk.py 2022-autumn-league-offshore.json < 2022_AL_offshore.htm
al-offshore-files: $(AL_OFFSHORE_FILES)

al-offshore-upload: $(AL_OFFSHORE_FILES)
	./ftp-upload.sh $(AL_OFFSHORE_FILES)

$(AL_INSHORE_FILES): 2022-autumn-league-inshore.json 2022_AL.htm scripts/chunk.py
	python scripts/chunk.py 2022-autumn-league-inshore.json < 2022_AL_inshore.htm
al-inshore-files: $(AL_INSHORE_FILES)

al-inshore-upload: $(AL_INSHORE_FILES)
	./ftp-upload.sh $(AL_INSHORE_FILES)

al-clean:
	rm -f $(AL_OFFSHORE_FILES) $(AL_INSHORE_FILES)
