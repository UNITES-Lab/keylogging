'use strict';

const express = require('express');
const serveStatic = require('serve-static');
const compression = require('compression');
const auth = require('basic-auth');

const setCustomCacheControl = (res, path) => {
    if (process.env.NODE_ENV !== 'production') {
        res.setHeader('Cache-Control', 'public, max-age=0')
    } else {
        if (serveStatic.mime.lookup(path) === 'text/html') {
            res.setHeader('Cache-Control', 'public, max-age=0')
        }
    }
}

module.exports = function(app, options) {

    app.use(compression());

    app.use(function(req, res, next) {
        if (options.user && options.password) {
            var user = auth(req);
            if (user === undefined || user['name'] !== options.user || user['pass'] !== options.password) {
                res.statusCode = 401;
                res.setHeader('WWW-Authenticate', 'Basic realm="node-serve"');
                res.end('Unauthorized');
            } else {
                next();
            }
        } else {
            next();
        }
    });

    app.use(function(req, res, next) {
        res.setHeader('Access-Control-Allow-Origin', '*');
        res.setHeader('Access-Control-Allow-Methods', 'GET,POST,OPTIONS,DELETE');
        res.setHeader('Access-Control-Allow-Headers', 'Origin, X-Requested-With, Content-Type, Accept');
        res.setHeader('Access-Control-Allow-Credentials', true);

        if (process.env.NODE_ENV !== 'production') {
            res.setHeader('X-Robots-Tag', "noindex, nofollow");
        }

        next();
    });

    app.use(serveStatic(options.path, {
        'index': ['index.html'],
        'dotfiles': 'ignore',
        'maxAge': '30d',
        'setHeaders': setCustomCacheControl
    }));

    app.get('*', function(req, res) {
        res.status(404).end();
    });

}