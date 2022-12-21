
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
	@wget -m ftp://$(FTP_USER):$(FTP_PASSWORD)@$(FTP_SERVER)/$(FTP_DIR)
	find backups/results.hyc.ie/ -name .listing -delete

require_admin_password:
ifndef ADMIN_USERNAME
	$(error ADMIN_USERNAME is not defined)
endif
ifndef ADMIN_PASSWORD
	$(error ADMIN_PASSWORD is not defined)
endif

ADMIN_YEARS := 2023 2022 2021 2020 2019 2018 2017 2016 2015 2014 2013
ADMIN_FILES := $(foreach year,$(ADMIN_YEARS),backups/admin/$(year)_open.csv backups/admin/$(year)_club.csv)

backups/admin/%.csv:
	@year=$$(echo $@ | sed 's|backups/admin/\(.*\)_.*.csv|\1|'); \
	event_type=$$(echo $@ | sed 's|backups/admin/.*_\(.*\).csv|\1|'); \
	echo "Generating $@"; \
	./scripts/admin/get-results --csv $$year $$event_type > $@

admin-backup: require_admin_password $(ADMIN_FILES)

admin-backup-clean:
	rm -f $(ADMIN_FILES)

summaries-backup: require_admin_password
	./scripts/admin/download-results-summaries ./backups/summaries/

AL_OFFSHORE_FILES := 2022_AL_class1.htm 2022_AL_class2.htm 2022_AL_class4.htm 2022_AL_class5.htm
AL_INSHORE_FILES := 2022_AL_class3.htm 2022_AL_h17.htm 2022_AL_pup.htm 2022_AL_squib.htm

$(AL_OFFSHORE_FILES): 2022-autumn-league-offshore.json 2022_AL_offshore.htm scripts/chunk.py
	python scripts/chunk.py 2022-autumn-league-offshore.json < 2022_AL_offshore.htm
al-offshore-files: $(AL_OFFSHORE_FILES)

al-offshore-upload: $(AL_OFFSHORE_FILES)
	./scripts/ftp-upload.sh $(AL_OFFSHORE_FILES)

$(AL_INSHORE_FILES): 2022-autumn-league-inshore.json 2022_AL_inshore.htm scripts/chunk.py
	python scripts/chunk.py 2022-autumn-league-inshore.json < 2022_AL_inshore.htm
al-inshore-files: $(AL_INSHORE_FILES)

al-inshore-upload: $(AL_INSHORE_FILES)
	./scripts/ftp-upload.sh $(AL_INSHORE_FILES)

al-clean:
	rm -f $(AL_OFFSHORE_FILES) $(AL_INSHORE_FILES)
