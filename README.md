# Chrome REST

Manipulate Chrome through a REST API.

## Install

To install Chrome REST just clone this repo and run `./script/bootstrap`.

## Start server

To start the Chrome REST server just run `./script/server`.

## API calls

### List tabs

`GET /api/tabs`

### Create a new tab

`POST /api/tabs`

```
{"url": "https://www.sourcelair.com/home"}
```

### Get tab info

`GET /api/tabs/:tabid`

### Update a tab

`PUT /api/tabs/:tabid`

```
{"url": "https://www.sourcelair.com/home"}
```

### Close a tab

`DELETE /api/tabs/:tabid`
