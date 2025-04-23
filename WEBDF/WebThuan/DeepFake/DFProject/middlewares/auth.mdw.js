export function isAuth(req,res,next){
    if(req.session.auth===false){
        req.session.retUrl=req.originalUrl;
        return res.redirect('/account/login');
    }
    next();
}

export function isAdmin(req,res,next){
    if(req.session.authUser.permission!==0){
        return res.render('403');
    }
    next();
}

export function isUser(req,res,next){
    if(req.session.authUser.permission!==1){
        return res.render('403');
    }
    next();
}
