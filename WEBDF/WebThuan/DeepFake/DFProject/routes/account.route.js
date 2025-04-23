import express from 'express'
import bcrypt from 'bcryptjs'
import moment from 'moment';
import userService from '../services/user.service.js';
import { isAuth } from '../middlewares/auth.mdw.js';

const router = express.Router();

router.get('/register', function (req,res){
    res.render('vwAccount/register');
});

router.get('/forgot', function (req,res){
  res.render('vwAccount/forgot');
});

router.get('/login', function (req,res){
    res.render('vwAccount/login');
});

router.post('/register', async function (req,res){
    const hash_password = bcrypt.hashSync(req.body.raw_password,8);
    const ymd_dob = moment(req.body.raw_dob,'DD/MM/YYYY').format('YYYY-MM-DD');
    const entity = {
        username: req.body.username,
        password: hash_password,
        name: req.body.name,
        email: req.body.email,
        dob: ymd_dob,
        permission: req.body.permission
    };
    const ret = await userService.add(entity);
    res.render('vwAccount/login');
});

router.post('/login', async function (req,res){
    const user = await userService.findByUserName(req.body.username);
    if (!user) {
      return res.render('vwAccount/login', {
        has_errors: true
      });
    }
  
    if (!bcrypt.compareSync(req.body.password, user.password)) {
      return res.render('vwAccount/login', {
        has_errors: true
      });
    }
    req.session.auth = true;
    req.session.authUser = user;
    const retUrl = req.session.retUrl || '/';
    req.session.retUrl = null;
    res.redirect(retUrl);
});

router.get('/is-available', async function (req,res){
    const username = req.query.username;
    const ret = await userService.findByUserName(username);
    if(!ret){
        return res.json(true);
    }
    res.json(false);
});

router.get('/profile',isAuth,function(req,res){
  res.render('vwAccount/profile',{
    user: req.session.authUser
  });
});

router.get('/update-password',isAuth,function(req,res){
  res.render('vwAccount/update-password',{
    user: req.session.authUser
  });
});

router.get('/logout', function(req,res){
  req.session.auth = false;
  req.session.authUser = null;
  req.session.retUrl = null;
  res.redirect('/');
});

router.post('/patch',async function (req,res) {
  const id = parseInt(req.body.id);
  const ymd_dob = moment(req.body.raw_dob,'DD/MM/YYYY').format('YYYY-MM-DD');
  const entity = {
    username: req.body.username,
    name: req.body.name,
    email: req.body.email,
    dob: ymd_dob,
};
  await userService.patch(id,entity);
  res.redirect('/');
});

router.post('/pat',async function (req,res) {
  const id = parseInt(req.body.id);
  const hash_password = bcrypt.hashSync(req.body.raw_password,8);
  const entity = {
    password: hash_password
};
  await userService.pat(id,entity);
  res.redirect('/');
});

router.get('/list', async function (req,res) {
  const list = await userService.findAll();

  list.sort((a, b) => a.id - b.id);

  res.render('vwAccount/list', {
      users: list
  });
});

router.post('/del',async function (req,res) { 
    const id = parseInt(req.body.id);
    await userService.del(id);
    res.redirect('/account/list');
});

export default router;