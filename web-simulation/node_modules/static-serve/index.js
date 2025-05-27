#!/usr/bin/env node

const chalk = require('chalk');
const program = require('commander');
const express = require('express');
const config = require('./config/express');
const app = new express();
const { exec } = require('child_process');

program
    .version('0.0.1')
    .arguments('<path>')
    .option('-p, --port <port>', 'the port where to serve the files')
    .option('-U, --user <user>', 'username for http auth')
    .option('-P, --password <password>', 'password for http auth')
    .action(function(path) {
        let options = {
            port: program.port || 8080,
            path: path,
            user: program.user,
            password: program.password
        }

        config(app, options);

        // start app
        app.listen(options.port, (error) => {
            if (!error) {
                let url = `http://localhost:${options.port}`
                console.log(chalk.green(`Running ${options.path} on port: ${options.port}`));
                console.log(chalk.bold.cyan(`Opening ${url}`));
                exec(`open ${url}`);
            }
        });

    })
    .parse(process.argv);