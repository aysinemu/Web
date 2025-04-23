import express from 'express'

const router = express.Router();

router.get('/', async function (req, res) {
    res.render('vwDeepfake/run', {
    });
});

export default router