from extract import UU

if __name__ == '__main__':
    from example.links import urls

    u = UU()
    # urls = [
    #     'http://www.caheb.gov.cn/system/2023/05/04/030224852.shtml',
    #     'https://www.thepaper.cn/newsDetail_forward_22896216',
    #     'https://www.jiemian.com/article/9369085.html',
    #     'http://fjnews.fjsen.com/2023-05/14/content_31314474.htm',
    #     'http://linyi.sdchina.com/show/4815751.html',
    #     'https://wh.zibo.gov.cn/gongkai/channel_c_5f9fa491ab327f36e4c13060_n_1605682651.0101/doc_6593b42151e0885ffbe043ce.html'
    # ]

    # urls = ['https://sd.dzwww.com/sdnews/202303/t20230321_11583301.htm']
    for ul in urls:
        print('url', ul)
        u.uu(url=ul)
        print('*' * 50)
