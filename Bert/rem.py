#!/usr/bin/ python
# -*- coding: utf-8 -*-
# @Author  : ysl
# @File    : clean.py

import re
import html as ht
from io import BytesIO
import requests
# from req import Req
from PIL import Image
from lxml import html
from config import inspection, default_tag_, static_source
from loguru import logger
from collections import Counter
from bs4 import BeautifulSoup
from extract.parse import Parse
from urllib.parse import urljoin
from config import img_size, static_img
# from parsel import Selector
from lxml.html.clean import Cleaner
from config import chinese_punc, default_tag


class RemoveUseless:
    def __init__(self):
        pass

    @classmethod
    def clean_article_html(cls, htmls):
        """Remove some common styles according to the rules"""
        htmls = cls.clean_jumbled_text(htmls)
        uncommon_tags = cls.complete_transformation(htmls)
        uncommon_tag = Counter(uncommon_tags)
        result = uncommon_tag.most_common(1)
        for _tag, count in result:
            htmls = htmls.replace(_tag, 'div')
        article_cleaner = Cleaner(style=True, javascript=True, )
        article_cleaner.javascript = True
        article_cleaner.style = True
        article_cleaner.allow_tags = default_tag
        article_cleaner.remove_unknown_tags = False
        return article_cleaner.clean_html(htmls)

    @staticmethod
    def complete_transformation(htmls):
        soup = BeautifulSoup(htmls, 'html.parser')
        uncommon_tags = list()
        for tag in soup.find_all():
            if tag.name not in default_tag_:
                uncommon_tags.append(tag.name)
        return uncommon_tags

    @staticmethod
    def clean_jumbled_text(htmls):
        for txt in static_source:
            htmls = htmls.replace(txt, '')
        return htmls

    @classmethod
    def second_filter(cls, select, tag, nm, zh_char=''):
        """Only the length judgment is used here for the time being, it should be reasonable to
        calculate a score or classification model for multiple dimensions - consider the loading speed"""
        zh_char_set = list()
        for class_tag in nm:
            xpp = '//*[@{}="{}"]'.format(tag, class_tag)
            uncertainty_node = select.xpath(xpp)
            for n in uncertainty_node:
                string_node = html.tostring(n, encoding='unicode')
                zh_char_set.append({"len": len(cls.zh_hans(string_node)), "node": n, "str": string_node})
        res = sorted(zh_char_set, key=lambda x: int(x.get('len')), reverse=True) if zh_char_set else []
        ratings = [{"index_%s" % tag: index, "score": cls.score(x.get('str')), 'x': x} for index, x in enumerate(res)]
        return ratings

    @classmethod
    def duel(cls, duel_score):
        return sorted(duel_score, key=lambda x: (-x[0], x[1]))[0]

    @classmethod
    def ratings_structured_data(cls, res, index, x) -> dict:
        """xx is a good fun  It is currently deprecated"""
        diff, score = res[0]['len'] - x['len'], cls.score(x.get('str'))
        xx_dit = {"index": index, "score": score, "difference": diff, "str": x['str']}
        return xx_dit

    @classmethod
    def score(cls, node_str):
        unknown_tags = re.findall(r'</[a-z]{1,3}>', node_str, re.S)
        lss = sorted([(len(two), two[0]) for two in cls.count_and_find_tag_p(unknown_tags)], key=lambda x: x[0],
                     reverse=True)
        lss.sort(key=lambda x: x[1])
        for i in range(1, len(lss)):
            if lss[i - 1][0] < lss[i][0] * 2:
                lss[i - 1], lss[i] = lss[i], lss[i - 1]
        return lss[0] if lss else (0, 0)

    @staticmethod
    def count_and_find_tag_p(lst):
        twos = []
        for i in range(len(lst) - 1):
            if lst[i] == '</p>' and lst[i + 1] == '</p>':
                if i == 0 or lst[i - 1] != '</p>':
                    twos.append([i, i + 1])
                else:
                    twos[-1].append(i + 1)
        return twos

    @classmethod
    def id_cls(cls, text, url):
        """
        xpath('//attribute::*')  xpath('//@class | //@id')
        这里只用了score来进行决斗⚔️如果效果不理想， 还可以加入 len值
        """
        article_lst = list()
        _select = cls.tree(text)
        select = cls.img_tag(_select, url)
        gen_tag = [(select.xpath('//@class'), 'class'), (select.xpath('//@id'), 'id')]
        for tag_cls_id, tag_nm in gen_tag:
            article = cls.second_filter(select, tag_nm, tag_cls_id)
            article_lst += article
        duel = sorted(article_lst, key=lambda x: (-x['score'][0], x['score'][1]))
        duel_winner = duel[0].get('x').get('str') if duel else None
        text_end = Parse.final_quality_inspection(duel_winner)
        return text_end

    @classmethod
    def deep_cleanse(cls, text):
        _select = cls.tree(text)
        nodes = _select.xpath('//@class | //@id')
        for node in nodes:
            print(node)

    @classmethod
    def img_tag(cls, element, req_url, upload_pic=False):
        img_s = element.xpath('//img')
        for img in img_s:
            src = img.attrib.get('src')
            src = cls.verify(req_url, src)
            if any(s in src for s in static_img):
                img.attrib['src'] = ''
            else:
                if upload_pic:
                    src = cls.upload_pics(src)
                img.attrib['src'] = src
        return element

    @classmethod
    def upload_pics(cls, src):
        return src

    @staticmethod
    def zh_hans(string_node):
        return re.compile(r'[\u4e00-\u9fa5]').findall(string_node)

    @staticmethod
    def image_recognition(url, status=1):
        # Asking for a link to the image, determining the size of the image, but it's a waste of time
        response = requests.get(url)
        image = Image.open(BytesIO(response.content))
        width, height = image.size
        if width <= img_size and height <= img_size:
            status = 0
            logger.warning('This is a static resource image: {}'.format(url))
        return status

    @classmethod
    def verify(cls, req_url, src):
        if 'http' in src:
            return src
        return cls.url_join(req_url, src)

    @staticmethod
    def url_join(req_ur: str, link: str):
        return urljoin(req_ur, link)

    @staticmethod
    def tree(text):
        return html.fromstring(text)


if __name__ == '__main__':
    r = RemoveUseless()
    b = """



<!DOCTYPE html>
<html lang="en">
  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
    <meta name="filetype" content="0">
    <meta name="publishedtype" content="1">
    <meta name="pagetype" content="1">
    <meta name="catalogs" content="18080"/>
    <meta name="contentid" content="3299508"/>
    <meta name="publishdate" content="2023-02-27"/>
    <meta name="author" content="朱建华"/>
    <meta name="editor" content="董博婷&#32;王秋韵&#32;周晔"/>
    <meta name="source" content="新华社"/>
    <meta name="keywords" content="总书记,买买,提依,依布,布热,十年两会·温暖记忆丨“种下石榴树，开出团结花”,人民,政协,政协网,政协报,人民政协报" />
    <meta name="description" content=";十年两会·温暖记忆丨“种下石榴树，开出团结花”,人民政协网是由人民政协报社主办，全方位报道国内外重大新闻和各级统战、政协工作最新动态，为各级政协组织履行职能服务，为广大政协委员参政议政服务，是政协工作者开展工作的有益帮手，政协委员参政议政的重要参考，社会各界了解人民政协的重要渠道。" />
    <title>十年两会·温暖记忆丨“种下石榴树，开出团结花”——人民政协网</title>
     <link rel="shortcut icon" href="/images/nIndexImage/favicon.ico" /> 
    <link rel="stylesheet" href="/css/nIndex_common.css" type="text/css" />
    <link rel="stylesheet" href="/css/nIndex_header.css" type="text/css" />
    <link rel="stylesheet" href="/css/c_header.css" type="text/css" />
    <link rel="stylesheet" href="/css/gbdetails.css" type="text/css" />
    <link rel="stylesheet" href="/css/footer.css" type="text/css" />
    <script src="/js/jquery-1.8.3.min.js" type="text/javascript"></script>
    <script type="text/javascript" src="/js/founder_mbdbc.js" charset="utf-8"></script>

    <script src="/js/scrolltopcontrol.js" type="text/javascript"></script>
    <script src="/js/jquery.soChange1.js"></script>
    <script src='/js/roller.js'></script>
    <script src="/js/js.js"></script>
    <script src="/js/listPagePublicJs.js"></script>
    <script src="/js/advPublicJs.js"></script>    
    <style>
      table{width:100%;}table tr td {
	border: solid 1px;
	vertical-align: middle;
}
      *{font-family: "微软雅黑", "Microsoft Yahei", "SimSun", "宋体", "Arial Narrow"};
      nav{margin-bottom:30px}

      .a_nav {

        margin-bottom: 20px;

      }
      .a_nav a {
        color: #fff;
        margin: 0;
        font-size: 16px;
        display: block;
        padding: 0 19px;
        height: 45px;
        line-height: 45px;
        float: left;
      }
      .a_nav a:hover{        text-decoration: underline;
      }
      .a_nav {
        width: 994px;
        height: 45px;
        overflow: hidden;
        padding: 0 15px;
        background: #E3241A;
      }
      .text_box p{
        margin:20px 0 0 0 !important;
      }
      .text_box p span{    background: #fff !important;}
      .text_box div {
        margin: 0 auto;
      }
      .text_box table tr td{border:solid 1px #ccc;}


    </style>
      </head>
  <body>
    <div class="c_header">
      <div  class="c_logo contentBar">
        <div class="logoLeft fl">
          <a href="http://www.rmzxb.com.cn/index.shtml"><img src="/images/nIndexImage/logo.jpg" alt=""></a>
        </div>
        <div class="c_title fl">首&#32;页</div>

<div class="search fr">
          <div class="info">读懂，最中国的民主</div>
          <form name="form1" method="get" action="http://apply.rmzxb.com/unicms/search/result" target="_blank" class="ss">
            <input type="hidden" name="SiteID" value="14"/>
            <input type="hidden" name="Sort" value="PublishDate"/>
            <input class="text_input" type="text" name="Query"  suggest="true" suggestsource="Search.suggest" placeholder="人民政协网" data-inputcolor="#9c9c9c" onFocus="this.value=''" onBlur="if(!value){value=defaultValue;}" />
            <div class="sub"><input type="submit" id="searchSubmit" value="" class="icon button_input"></div>
          </form>
        </div>
      </div>
    </div>
    <div class="fullBar" style="background:#E3241A">
      <!--   有事漫商量、委员讲堂 导航-->

      <!--   首页 导航-->

<div class="a_nav contentBar">


        <a href="http://www.rmzxb.com.cn/index.shtml">首 页</a>


        <a href="/yw_n/index.shtml" target="_blank">要闻</a>


        <a href="/yl_n/index.shtml" target="_blank">要论</a>

        <a href="/xs/index.shtml" target="_blank">协商</a>

        <a href="/tz/index.shtml" target="_blank">统战</a>
        <a href="/dp/index.shtml" target="_blank">党派</a>
        <a href="/wyjt/index.shtml" target="_blank">委员讲堂</a>
        <a href="/ll/index.shtml" target="_blank">理论</a>
        <a href="/rs/index.shtml" target="_blank">人事</a>
        <a href="/sh/index.shtml" target="_blank">社会</a>
        <a href="/fz/index.shtml" target="_blank">法治</a>
        <a href="/sp_n/index.shtml" target="_blank">视频</a>
        <a href="/wh/index.shtml" target="_blank">文化</a>
      </div>

      <!--    导航-->

      <!--   要闻 导航-->

      <!--   要论 导航-->

      <!--   协商 导航-->

      <!--   统战 导航-->

      <!--  党派 导航-->

      <!--  理论 导航-->

      <!--  社会 导航-->

      <!--  法治 导航-->

      <!--  文化 导航-->

      <!--  春秋 导航-->

      <!--  扶贫 导航-->

      <!--  经济 导航-->

      <!--  健康 导航-->

      <!--  生态 导航-->

      <!--  科技 导航-->

      <!--  教育 导航-->


      <!--  书画 导航-->

      <!--  旅游 导航-->

      <!--  公益 导航-->

      <!--  港澳 导航-->

      <!--  台湾 导航-->

      <!--  侨声 导航-->

      <!--  电影 导航-->

      <!--  农业 导航-->

      <!--  人事 导航-->

      <!--  学习 导航-->

      <!--  一带一路 导航-->

      <!--  视频 导航-->

      <!--  收藏 导航-->

      <!--  习近平报道专集 导航-->

      <!--  其他 导航-->

    </div>




    <div id="content">
      <div class="pv_box m_p ov_hi">
        <div class="bw_1024">


          <h1 class="pv_title_2">
            <span class="site fl">
              <a href="http://www.rmzxb.com.cn/index.shtml">首页</a>><a href="/xsy/yw/">要闻</a>
            </span>
          </h1>

          <div class="pa_0_5_0_10">
            <h1 class="Content_title" id="hh">

              <span id="a" style="">十年两会·温暖记忆丨“种下石榴树，开出团结花”</span>
            </h1>

            <script>/*jQuery('#hh').width(jQuery('#a').width());*/</script>
            <div style="position: relative;">
            <div class="Remark">
              <span>2023年02月27日&#32;09:15&nbsp; | &nbsp;作者:董博婷&#32;王秋韵&#32;周晔 &nbsp;| &nbsp;来源：<a href="http://www.baidu.com/baidu?word=新华社" target="_blank">新华社</a></span>
              <span class="fr">
                 <!--分享 BEGIN-->
                <div class="share">
                  <div class="s-wb" title="分享到微博"></div>
                  <div class="s-q" title="分享到QQ空间"></div>
                  <div class="share-wx-item" title="分享到微信"></div>
                  <div class="wx-ewm" id="code" style="display: none;"></div>

                </div>
                <!--分享 END-->
              </span><span class="fr">分享到：<img src="http://www.rmzxb.com.cn/images/fx.jpg" />&nbsp;</span>
            </div>
            <div class="text_box">

                <p style="text-indent: 2em; text-align: left;">新华社乌鲁木齐2月26日电<strong>题：“种下石榴树，开出团结花”</strong></p><p style="text-indent: 2em; text-align: left;">新华社记者董博婷、王秋韵、周晔</p><p style="text-indent: 2em; text-align: left;">见到新疆和田地区策勒县巴什玉吉买村党支部书记买买提依布热依木·买买提明时，他站在南疆干燥热烈的春风里，笑着朝我们猛劲儿挥手。</p><p style="text-indent: 2em; text-align: left;">“我的朋友们，欢迎你们！”操着流利了许多的普通话，他抓着几个丰收季存下的大石榴往我们手里塞。</p><p style="text-indent: 2em; text-align: left;">“这是‘团结果’‘幸福果’嘞！”说起一段关于石榴的往事，买买提依布热依木笑得合不拢嘴。</p><p style="text-indent: 2em; text-align: left;">那是2017年3月10日，习近平总书记来到十二届全国人大五次会议新疆代表团参加审议。买买提依布热依木就落实惠民政策等发言后，对总书记说：“我还想汇报一件事。”</p><p style="text-indent: 2em; text-align: left;">“你讲。”总书记用鼓励的眼神望着他。</p><p style="text-indent: 2em; text-align: left;">“您不久前给库尔班大叔的家人回了信。他们一家人非常高兴，托我带来几张照片给您看，还说一定像总书记信中嘱托的那样，永远记得党的恩情，像石榴籽一样紧紧地抱在一起。”</p><p style="text-indent: 2em; text-align: left;">总书记一边端详照片一边微笑着说：“真是人丁兴旺啊。”</p><p style="text-indent: 2em; text-align: left;">总书记关切地问：“你家里有没有结对的？”</p><p style="text-indent: 2em; text-align: left;">“有有有”“自从开始搞结对认亲活动，汉族的同志来了，我们也主动找他们，我们一块劳动，一家亲。”买买提依布热依木一下打开了“话匣子”。</p><p style="text-indent: 2em; text-align: left;">听了他的回答，总书记欣慰地点点头，微笑着说：“结对认亲能够很认真、很讲实效地开展起来，对促进民族团结很有意义。”</p><p style="text-indent: 2em; text-align: left;">总书记的话语，让买买提依布热依木想到了远在家乡的汉族“亲戚”，在他来京开会的这段时间，正帮他打理着家里的蔬菜大棚。</p><p style="text-indent: 2em; text-align: left;">他不禁有些激动，亮起嗓门说了声：“党的政策亚克西！”</p><p style="text-indent: 2em; text-align: left;">习近平总书记回应他：亚克西！</p><p style="text-indent: 2em; text-align: left;">回到新疆后，买买提依布热依木走村串户，把总书记对新疆发展的重视和对百姓生活的关心讲给乡亲们听；他走进学校，给孩子们讲“石榴籽”的寓意；他创办了“石榴花人民调解工作室”，给大家解决困难、调解矛盾……几年过去，他发现村民间的关系越来越和谐，村干部的工作越来越顺手。</p><p style="text-indent: 2em; text-align: left;">走在路上，买买提依布热依木一会儿指着成片的石榴树，介绍石榴酒厂的红火，一会儿又开心地说起民族团结的故事。</p><p style="text-indent: 2em; text-align: left;">四五个孩子结伴从我们身边跑过，亲切地喊他“代表爸爸”。路过的村民也簇拥过来，和“买书记”唠上几句，问的尽是村里今年还有什么发展规划。</p><p style="text-indent: 2em; text-align: left;">看着围拢过来的村民，买买提依布热依木说：“习近平总书记多次强调‘民族团结是发展进步的基石’，只有安定团结，各项生产生活才能有序开展。咱们大家一定要齐心协力，种下石榴树，开出团结花，结出幸福果！”</p><p style="text-indent: 2em; text-align: left;">石榴的栽种季就在眼前，村里到处都是忙碌的景象。待到五六月份，火红的石榴花又将开遍这片绿洲。</p><p style="text-indent: 2em; text-align: left;">买买提依布热依木的眼中充满憧憬，他用骄傲的口吻告诉我们：“从和田到若羌的铁路开通了，内地的客商来往更方便了，全国的朋友都能尝到我们的石榴有多甜！”（完）</p><p><br style="text-indent: 2em; text-align: left;"/></p>
               </div>

            <p class="Editor">编辑：朱建华 </p>

            <div class="Paging">








            </div>

            <!--<z:if condition="${Article.Keyword!=null}"><p class="Keyword">关键词：${Article.Keyword}</p></z:if>-->


            <!--政协号客户端下载-->

<style> .zxh:hover{color:#333;}</style>
            <div style="background:#F9F9F9;padding:50px 30px;text-align:center;width:302px;margin:13px auto 5px auto"><a  href="http://www.rmzxb.com.cn/zxh/images/zxh.jpg" target="_blank" style="font-size:19px;display:block;" class="zxh"><img src="/images/nIndexImage/zxh_icon.png" alt="" style="margin-bottom:15px;"><br>人民政协报<span style="font-weight:bold">政协号</span>客户端下载 ></a></div>
            </div>
            <!-- 分享结束 -->
          </div>
        </div>
      </div>
       <script src="/js/jquery_002.js" type="text/javascript"></script>
    <script src="/js/qrcode.js"  type="text/javascript"></script>
    <script>    
      var href1=window.location.href;
      console.log(href1);
      var title = $.trim($("#a").text());
      /*修改点击a弹出*/
      var wbSrc = 'http://service.weibo.com/share/share.php?url=' + href1 + '&title=' + title;
      var qqSrc = 'http://sns.qzone.qq.com/cgi-bin/qzshare/cgi_qzshare_onekey?url=' + href1 + '&title=' + title;
      var wbHtml = '<a style="width:100%;" target="_blank"  href="'+wbSrc+'"></a>';
      $(".s-wb").html(wbHtml)
      var qHtml = '<a style="width:100%;" target="_blank"  href="'+qqSrc+'"></a>';
      $(".s-q").html(qHtml);
      $(".copyright .right").hide();
      /*修改点击a弹出*/
      $(".share-wx-item").on("mouseover", function () {
        $(".wx-ewm").stop(true, true).slideDown();
      }).on("mouseleave", function () {
        $(".wx-ewm").stop(true, true).slideUp();
      });
      $(document).ready(function(){
        var href1=window.location.href;
        $("#code").qrcode({
          width:200, //宽度
          height:200, //高度
          text: href1, //任意内容

        });
      })
    </script>
          <!--微信分享引入	JSSDK-->
    <script type="text/javascript" src="http://res.wx.qq.com/open/js/jweixin-1.4.0.js"></script>
    <!--<script type="text/javascript" src="http://mobile.rmzxb.com.cn/jweixin.js"></script>-->
    <script>
      url = location.href.split('#')[0];

      url = encodeURIComponent(url);
      window.wxShare = function(options){
        if(!window['wx']){
          return;
        }
        options = $.extend({},{
          title: '十年两会·温暖记忆丨“种下石榴树，开出团结花”', // 分享标题
          desc: '人民政协网--读懂，最中国的民主。www.rmzxb.com.cn', // 分享描述
          link: location.href, // 分享链接，该链接域名或路径必须与当前页面对应的公众号JS安全域名一致
          imgUrl: 'http://mobile.rmzxb.com.cn/wxLogo.png', // 分享图标
          trigger: function (res) {
          },
          cancel: function (res) {
          },
          success: function (res) {
          },
          fail: function (res) {
          }
        },options);

        window.wxShareConfig = options;

        $.ajax({
          type : "get",
          url : "http://mobile.rmzxb.com.cn/jssdk.php?url="+url,
          dataType : "jsonp",
          jsonp: "callback",
          jsonpCallback:"success_jsonpCallback",
          success : function(data){
            wx.config({
              appId: data.appId,
              timestamp: data.timestamp,
              nonceStr: data.nonceStr,
              signature: data.signature,
              jsApiList: [
                'onMenuShareTimeline',//
                'onMenuShareAppMessage',
                'onMenuShareQQ',
                'onMenuShareWeibo',
                'onMenuShareQZone'

              ]
            });
            wx.ready(function () {

              wx.onMenuShareTimeline(window.wxShareConfig);
              wx.onMenuShareAppMessage(window.wxShareConfig);
              wx.onMenuShareQQ(window.wxShareConfig);//分享给手机QQ
              wx.onMenuShareWeibo(window.wxShareConfig);//分享腾讯微博
              wx.onMenuShareQZone(window.wxShareConfig);//分享到QQ空间



            });
            wx.error(function (res) {
              //alert(res.errMsg);//错误提示

            });
          },
          error:function(data){
            //alert("连接失败！");
          }
        });
      }
      window.wxShare({
        imgUrl:'http://mobile.rmzxb.com.cn/wxLogo.png'
      });
    </script>
      <script>/*baiduStat*/
var _hmt=_hmt||[];
(function() {
   var hm=document.createElement("script");
   hm.src="//hm.baidu.com/hm.js?b15ab1eded7d23043d92a4d0ce2872a6";
   var s=document.getElementsByTagName("script")[0];
   s.parentNode.insertBefore(hm, s);
})();
        /*baidu zhudongtuisong*/
(function() {
	var bp=document.createElement('script');
	bp.src='//push.zhanzhang.baidu.com/push.js';
	var s=document.getElementsByTagName("script")[0];
	s.parentNode.insertBefore(bp, s);
})();
        var _hmt = _hmt || [];
(function() {
  var hm = document.createElement("script");
  hm.src = "//hm.baidu.com/hm.js?7dd9028205f42ce083a21da5c0c8e8f6";
  var s = document.getElementsByTagName("script")[0]; 
  s.parentNode.insertBefore(hm, s);
})();
/**/
/*baiduStat*/</script>
      <a  id="gotop"  href="javascript:scroll(0,0)"  style="display: none;"></a>
    </div>
    <!--footer公用区块开始-->

<style>
 #footer {
    padding-top:20px;
    width:100%;
    border-top:solid 1px #EFEFEF;
    height:445px;
    position:relative;
}
#footer .links {
    margin:0 auto;
    overflow:hidden;
}
#footer h3 {
    font-size:16px;
    margin-bottom:9px;
    font-weight:bold;
}
#footer .fLShow {
    font-size:13px;
    height:33px;
    line-height:33px;
}
#footer .fLShow a {
    padding:0 6px;
}
#footer .news-link {
    line-height:25px;
    margin-bottom:25px;
}
#footer .news-link a {
    font-size:13px;
    padding-right:13px;
}
#footer .copyRightInfo {
    text-align:center;
}
#footer .copyRightInfo .connect {
    line-height:13px;
    height:13px;
    margin-bottom:25px;
    font-weight:bold;
}
#footer .copyRightInfo .connect .dec {
    padding-right:6px;
}
#footer .copyRightInfo .connect a {
    color:#333;
    font-size:12px;
       font-weight:bold;
    display:inline-block;
    padding:0px 3px;
}
#footer .copyRightInfo .connect a:hover{
    color: #E3241A;
}
#footer .copyRightInfo .announce {
    line-height:22px;
}
#footer .buttomIconDiv img {
    height:35px;
    margin-top:20px;
    margin-bottom:20px;
    margin-left:12px;
}
#footer .buttomIconDiv {
    width:200px;
    margin:0 auto;
}
  #footer .fLShow a,.connect a{font-size: 14px !important;}
  #footer .news-link a {
    font-size: 14px;
    padding-right: 12px;
  }#footer .buttomIconDiv{width:253px !important;}
  .announce{font-size: 14px;}
  .announce a{display:inline-block;text-decoration:none;height:20px;line-height:20px; color:#777;font-size:14px;}
  #footer .copyRightInfo .announce {
    line-height: 25px;
  }
</style>
<div id="footer">
  <div class="links contentBar">
    <h3>友情链接：</h3>
    <div class="news-link">
      <a href="http://www.npc.gov.cn/" target="_blank">全国人大</a>
      <a href="https://www.gov.cn/" target="_blank">中国政府网</a>
      <a href="http://www.cppcc.gov.cn/" target="_blank">中国政协网</a>
      <a href="http://en.cppcc.gov.cn/" target="_blank">全国政协英文网站</a>
      <a href="http://www.zytzb.gov.cn/" target="_blank">中共中央统战部</a>
      <a href="http://www.minge.gov.cn" target="_blank">民革</a>
      <a href="http://www.dem-league.org.cn/" target="_blank">民盟</a>
      <a href="http://www.cndca.org.cn/" target="_blank">民建</a>
      <a href="http://www.mj.org.cn/" target="_blank">民进</a>
      <a href="http://www.ngd.org.cn/" target="_blank">农工党</a>
      <a href="http://www.zg.org.cn/" target="_blank">致公党</a>
      <a href="http://www.93.gov.cn/" target="_blank">九三学社</a>
      <a href="http://www.taimeng.org.cn/" target="_blank">台盟</a>
      <a href="http://www.acfic.org.cn/" target="_blank">全国工商联</a><br>
      <a href="https://www.zysy.org.cn/" target="_blank">中央社会主义学院</a>
      <a href="http://www.zgjx.cn/" target="_blank">中国记协</a><br>
      <a href="http://www.people.com.cn/" target="_blank">人民网</a>
      <a href="http://www.xinhuanet.com/" target="_blank">新华网</a> 
      <a href="http://www.china.com.cn/" target="_blank">中国网</a> 
      <a href="https://www.cri.cn/" target="_blank">国际在线</a> 
      <a href="https://cn.chinadaily.com.cn/" target="_blank">中国日报网</a> 
      <a href="https://www.cctv.com/" target="_blank">央视网</a> 
      <a href="https://www.youth.cn/" target="_blank">中国青年网</a> 
      <a href="http://www.ce.cn/" target="_blank">中国经济网</a> 
      <a href="http://www.taiwan.cn/" target="_blank">中国台湾网</a>
      <a href="http://www.tibet.cn/" target="_blank">中国西藏网</a>
      <a href="https://www.cnr.cn/" target="_blank">央广网</a> 
      <a href="https://www.gmw.cn/" target="_blank">光明网</a> 
      <a href="http://www.81.cn/" target="_blank">中国军网</a> 
      <a href="https://www.chinanews.com.cn/" target="_blank">中国新闻网</a><br> 
      <a href="http://www.legaldaily.com.cn/" target="_blank">法治网</a>
      <a href="http://www.workercn.cn/" target="_blank">中工网</a>
      <a href="http://www.k618.cn/" target="_blank">未来网</a> 
      <a href="http://www.tuanjiewang.cn/" target="_blank">团结网</a> 
    </div>
    <div class="copyRightInfo">
      <p class="connect">
        <a href="http://www.rmzxb.com.cn/aboutus/#bar1" target="_blank" class="dec">关于我们</a>|
        <a href="http://www.rmzxb.com.cn/aboutus/#bar3" target="_blank" class="dec">广告服务</a>|
        <a href="http://www.rmzxb.com.cn/aboutus/#bar4" target="_blank" class="dec">网站律师</a>|
        <a href="http://www.rmzxb.com.cn/aboutus/#bar4" target="_blank" class="dec">网站声明</a>|
        <a href="http://www.rmzxb.com.cn/aboutus/#bar5" target="_blank">联系我们</a>
      </p>

      <p class="announce">
        中国人民政治协商会议全国委员会主管·人民政协报社主办<br>法律顾问：北京市兰台律师事务所<br> 本网站所刊登的新闻和各种信息未经协议授权不得使用或转载<br>
        <a target="_blank" href="/zt/gbdsjmzzjyxkz/index.shtml">广播电视节目制作经营许可证（京）字第20070号</a>&nbsp;&nbsp;<a href="https://beian.miit.gov.cn/#/Integrated/index" target="_blank"  style="">京ICP备09078172号</a><br>
        <a target="_blank" href="http://www.beian.gov.cn/portal/registerSystemInfo?recordcode=11010802035063">京公网安备 11010802035063号&nbsp;&nbsp;&nbsp;</a>互联网新闻信息服务许可证：10120170079<br>
        违法和不良信息举报电话：010-88146989&nbsp;&nbsp;&nbsp;举报邮箱：<a href="mailto:rmzxw@rmzxb.com.cn" target="_blank" style="color:#333;">rmzxw@rmzxb.com.cn</a><br>
        <a href="https://www.12377.cn/" target="_blank">违法和不良信息举报中心</a>
      </p>
    </div>
    <div class="buttomIconDiv">
      <a target="_blank" href="http://www.beian.gov.cn/portal/registerSystemInfo?recordcode=11010802035063" style="text-decoration:none;height:20px;line-height:20px;"><img src="/images/nIndexImage/jgwab.png" style="height:30px;"/></a>
      <script type="text/javascript">document.write(unescape("%3Cspan id='_ideConac' %3E%3C/span%3E%3Cscript src='http://dcs.conac.cn/js/33/000/0000/60811474/CA330000000608114740001.js' type='text/javascript'%3E%3C/script%3E"));</script>
      <img id="placeHolder" src="http://www.rmzxb.com.cn/images/indexBottomIcon_03.jpg">
    </div>
    <div style="text-align: center;width: 300px;margin: 0 auto;margin-top: -12px;/* padding: 20px 0; */margin-bottom: 9px;">

    </div>
  </div>

  <a  id="gotop"  href="javascript:scroll(0,0)"  style="display: none;"></a>


</div>
    <!--footer公用区块结束-->
    <!--index底部公用区块开始-->


<!--公用底部代码块开始-->
<!--cms统计开始-->
<div style="display:none">
	<script type="text/javascript">document.write(unescape("%3Cscript src='http://info.rmzxb.com.cn:8088/webdig.js?z=19' type='text/javascript'%3E%3C/script%3E"));</script>
	<script type="text/javascript">wd_paramtracker("_wdxid=000000000000000000000000000000000000000000")</script>
</div>
<!--cms统计结束-->

<!---->

<!--baidu广告开始
baidu广告结束-->

<!--baidu广告2开始-->

<div class="advContent"><script type="text/javascript">var cpro_id="u2131508";</script><script src=" http://su.bdimg.com/static/dspui/js/uf.js" type="text/javascript"></script></div>
<!--baidu广告2结束-->

<!--原创认证-->
<script src="https://yb-public.oss-cn-shanghai.aliyuncs.com/yb-js/rmzxb.js" type="text/javascript"></script>
<!--百度统计开始--这一段移到了前面
百度统计结束-->

<!--百度主动推送-->
<script>
(function(){
    var bp = document.createElement('script');
    bp.src = '//push.zhanzhang.baidu.com/push.js';
    var s = document.getElementsByTagName("script")[0];
    s.parentNode.insertBefore(bp, s);
})();
</script>



<!--公用底部代码块结束-->

    <!--index底部公用区块结束-->

    <!--人民日报统计收集-->
    <script language="javascript">
      var _paq = _paq || [];
      window['_paq'] = _paq;
      _paq.push(['appkey', 'UAR-000321_719']);
      _paq.push(['cata', '18080']);
      _paq.push(['attr', 'itemid='+3299508]);
      _paq.push(['trackPV']);
      (function() {
        var pa = document.createElement('script'); pa.type = 'text/javascript'; pa.async = true
        ;
        pa.src = ('https:' == document.location.protocol ? 'https://' : 'http://') + 'rev.uar.hubpd.com/agent/pa.js';
        var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(pa, s);
      })();
    </script>
  <!-- App=ZCMS(ZCMS内容管理系统) 2.4.27177,CostTime=4,PublishDate=2023-02-27 09:34:55 -->
</body>
</html>
    """
    end = r.clean_article_html(b)
    print(end.replace('\n', '').replace(' ', ''))
    # print(r.id_cls(a))
