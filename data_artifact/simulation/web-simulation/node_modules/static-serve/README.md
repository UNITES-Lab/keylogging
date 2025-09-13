# static-serve

A simple development server for static html.

`static-serve` serves your static html files from the root you specify with gzip compression and optional http authentication.


## Installation

    $ npm install static-serve -g

## Usage

    $ static-serve /path/to/html

### Browse

Go to `http://localhost:8080/`

### Options

  * `-p` Port to use, defaults to 8080
  * `-U` Username for HTTP auth, won't be activated if the field is not set
  * `-P` Password for HTTP auth, won't be activated if the field is not set