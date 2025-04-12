import VueRouter from 'vue-router'

import wbAnalyze from '../pages/wbAnalyze';
import home from '../pages/home';
import login from '../pages/login';
import blog_detail from '../pages/blog_detail';
import person_list from '../pages/person_list';
import all_view from '../pages/all_view';
import hot from '../pages/hot';
import WXAnalyze from '../pages/WXAnalyze';
import RmAnalyze from '../pages/RmAnalyze';
import TBAnalyze from '../pages/TBAnalyze';
import tb_detail from '../pages/tb_detail';
import User from '../pages/User';
import Rumor from '../pages/Rumor';
import RumorAnalyse from '../pages/RumorAnalyse';
import all_detail from '../pages/all_detail';
import topic_person_list from '../pages/topic_person_list';
import mainscreen from "../pages/mainscreen"

export default new VueRouter({
    routes: [{
            path: "/",
            component: home,
            meta: {
                title: "智析万象"
            }
        },
        {
            path: "/home",
            component: home,
            meta: {
                title: "智析万象"
            }
        },
        {
            path: "/mainscreen",
            component: mainscreen,
            meta: {
                title: "舆情系统大屏"
            }
        },
        {
            path: "/all_view",
            name: 'all_view',
            component: all_view,
            meta: {
                title: "总览"
            }
        },
        {
            path: "/all_detail",
            name: 'all_detail',
            component:  all_detail,
            meta: {
                title: "总览详情"
            }
        },
        
        {
            path: "/topic_person_list",
            name: 'topic_person_list',
            component:  topic_person_list,
            meta: {
                title: "总览人员详情"
            }
        },
        {
            path: "/Rumor",
            name: 'Rumor',
            component: Rumor,
            meta: {
                title: "谣言"
            }
        },
        
        {
            path: "/rumorAnalyse",
            name: 'rumorAnalyse',
            component: RumorAnalyse,
            meta: {
                title: "谣言分析"
            }
        },
        {
            path: "/hot",
            component: hot,
            meta: {
                title: "热点事件"
            }
        },
        {
            path: "/wb",
            component: wbAnalyze,
            meta: {
                title: "微博舆情分析"
            }
        },
        {
            path: "/wx",
            name: 'wx',
            component: WXAnalyze,
            meta: {
                title: "微信舆情分析"
            }
        },
        {
            path: "/rm",
            name: 'rm',
            component: RmAnalyze,
            meta: {
                title: "人民网舆情分析"
            }
        },
        {
            path: "/tb",
            name: 'tb',
            component: TBAnalyze,
            meta: {
                title: "贴吧舆情分析"
            }
        },
        {
            path: "/login",
            name: 'login',
            component: login,
            meta: {
                title: "登录注册"
            }
        },
        {
            path: "/blog_detail",
            component: blog_detail,
            meta: {
                title: "博文详情"
            }
        },
        {
            path: "/tb_detail",
            component: tb_detail,
            meta: {
                title: "贴吧详情"
            }
        },
        {
            path: "/person_list",
            component: person_list,
            meta: {
                title: "用户列表"
            }
        },
        {
            path: "/user",
            component: User,
            meta: {
                title: "用户登陆注册"
            }
        }
        
    ],
    mode: "history"
})