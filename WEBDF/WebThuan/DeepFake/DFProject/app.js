import express from 'express';
import {dirname, format} from 'path'
import {fileURLToPath} from 'url'
import {engine} from 'express-handlebars';
import accountRouter from './routes/account.route.js'
import numeral from 'numeral';
import hbs_section from'express-handlebars-sections'
import session from 'express-session';
import { isAdmin,isAuth,isUser} from './middlewares/auth.mdw.js';
import Handlebars from 'handlebars';
import deepfakeRouter from './routes/deepfake.route.js'

const app = express();
app.set('trust proxy', 1) // trust first proxy
app.use(session({
  secret: 'SECRET_KEY',
  resave: false,
  saveUninitialized: true,
  cookie: { }
}))

app.engine('hbs', engine({
    extname: 'hbs',
    helpers: {
        format_number(value){
            return numeral(value).format('0,0') + ' VND';
        },
        fillHtmlContent: hbs_section()
    }
}));
app.set('view engine', 'hbs');
app.set('views', './views');

app.use('/static',express.static('static'));

app.use(async function(req,res,next){
    if(req.session.auth === undefined){
        req.session.auth = false;
    }
    res.locals.auth = req.session.auth;
    res.locals.authUser = req.session.authUser;
    next();
});

app.use(express.urlencoded({
    extended: true
}))

Handlebars.registerHelper('eq', function(a, b) {
    return a === b; 
});

Handlebars.registerHelper("or", function (a, b) {
    return a || b;
  });

Handlebars.registerHelper('array', function (...args) {
    return args.slice(0, -1);
});


Handlebars.registerHelper('inArray', function (value, array) {
    return array.includes(value);
});

Handlebars.registerHelper('and', function (a, b) {
    return a && b;
});

// function rootHandler (req, res) {
//     res.send('Hello World!');
// }

// function serverStartedHander(){
//     console.log('Server started on http://localhost:3000');
// }
app.use('/account', accountRouter);

app.use('/admin/deepfake',isAuth,deepfakeRouter);

app.get('/', function (req, res) {
    console.log(req.session.auth);
    const number = Math.floor(Math.random()*40);
    // res.render('home', {
    //     layout:false,
    //     randomNumber : number
    // });
    res.render('home', {
        randomNumber : number
    });
});

app.listen(3000, function (){console.log('Server started on http://localhost:3000');});

const __dirname = dirname(fileURLToPath(import.meta.url));
app.get('/test',function (req, res) {res.sendFile(__dirname + '/test.html');});
