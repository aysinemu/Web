import db from "../utils/db.js";

export default {
    findAll(){
        // return[
        //     {CatID: 1,CatName: 'Laptop'},
        //     {CatID: 2,CatName: 'TV'},
        //     {CatID: 3,CatName: 'Mobile'},
        // ];
        return db('users');
    },
    add(entity){
        return db('users').insert(entity);
    },
    findByUserName(username){
        return db('users').where('username',username).first();
    },
    patch(id, entity){
        return db('users').where('id', id).update(entity);
    },
    pat(id, entity){
        return db('users').where('id', id).update(entity);
    },
    del(id){
        return db('users').where('id', id).del();
    },
}