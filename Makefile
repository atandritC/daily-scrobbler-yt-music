build:
	docker build -t scrobbler .

run:
	docker run --env-file=.env scrobbler

start: build run
