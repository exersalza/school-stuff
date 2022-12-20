"use strict";
const nodemailer = require("nodemailer");
let express = require('express');
let app = express();

app.get('/v1/burn/:id/:comp/:value/:hard', function (req, res) {
    res.send({message: 'succeed'});
    if (Number(req.params.hard)) {
        main("Hard limits Reached", req.params.value).catch((reason) => {console.log(reason)})
    }
    res.end();
})

let server = app.listen(8000, function () {
    let host = server.address().address
    let port = server.address().port
    console.log("Example app listening at http://%s:%s", host, port)
})

// async..await is not allowed in global scope, must use a wrapper
async function main(subject, message) {
    // Generate test SMTP service account from ethereal.email
    // Only needed if you don't have a real mail account for testing
    let testAccount = await nodemailer.createTestAccount();

    // create reusable transporter object using the default SMTP transport
    let transporter = nodemailer.createTransport({
        host: "smtp.ethereal.email",
        port: 587,
        secure: false, // true for 465, false for other ports
        auth: {
            user: testAccount.user, // generated ethereal user
            pass: testAccount.pass, // generated ethereal password
        },
    });

    // send mail with defined transport object
    let info = await transporter.sendMail({
        from: '"Monitoring Administration" <foo@example.com>', // sender address
        to: "admin@knxr.dev", // list of receivers
        subject: subject, // Subject line
        text: message // plain text body
    });

    console.log("Message sent: %s", info.messageId);
    // Message sent: <b658f8ca-6296-ccf4-8306-87d57a0b4321@example.com>

    // Preview only available when sending through an Ethereal account
    console.log("Preview URL: %s", nodemailer.getTestMessageUrl(info));
    // Preview URL: https://ethereal.email/message/WaQKMgKddxQDoou...
}