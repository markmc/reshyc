
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

FTP_SERVER := results.hyc.ie
FTP_USER := hyc.ie_results

require_password:
ifndef FTP_PASSWORD
	$(error FTP_PASSWORD is not defined)
endif

backup: require_password
	wget -m ftp://$(FTP_USER):$(FTP_PASSWORD)@$(FTP_SERVER)/reshyc

AL_FILES := 2022_AL_class1.htm 2022_AL_class2.htm 2022_AL_class3.htm 2022_AL_class4.htm 2022_AL_class5.htm 2022_AL_h17.htm 2022_AL_pup.htm 2022_AL_squib.htm

$(AL_FILES): 2022-autumn-league.json 2022_AL.htm scripts/chunk.py
	python scripts/chunk.py 2022-autumn-league.json < 2022_AL.htm
al-files: $(AL_FILES)

al-clean:
	rm -f $(AL_FILES)
