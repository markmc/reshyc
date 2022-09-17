
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
