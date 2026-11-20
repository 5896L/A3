# from .models import Book
#
# def fun_get_books():
#     books = Book.objects.all() #返回QuerySet
#     total_rows=books.count()
#     print('查询到'+str(total_rows)+'条记录')
#     for book in books:
#         print(book.NAME, book.AUTHOR, book.PUBLISHER)
#     print('')
#
# def fun_insert_book():
#     NewBook = Book()
#     NewBook.NAME = '水浒传'
#     NewBook.AUTHOR = '施耐庵，罗贯中'
#     NewBook.PUBLISHER = '中华书局'
#     NewBook.PUBLISHTIME = '2005-4-1'
#     NewBook.PRODUCTNO = '9787101046137'
#     NewBook.SATETYSTOCKLEVEL = '10'
#     NewBook.ORIGINALPRICE = '19'
#     NewBook.NOWPRICE = '14.3'
#     NewBook.DISCOUNT = '7.5'
#     NewBook.DESCRIPTION = '''
#             《水浒传》是宋江起义故事在民间长期流传基础上产生出来的，吸收了民间文学的营养。
#             《水浒传》是我国人民最喜爱的古典长篇白话小说之一。它产生于明代，是在宋、元以来有关水浒的故事、话本、戏曲的基础上，由作者加工整理、创作而成的。
#             全书以宋江领导的农民起义为主要题材，艺术地再现了中国古代人民反抗压迫、英勇斗争的悲壮画卷。
#             作品充分暴露了封建统治阶级的腐朽和残暴，揭露了当时尖锐对立的社会矛盾和“官逼民反”的残酷现实，成功地塑造了鲁智深、李逵、武松、林冲、阮小七等一批英雄人物。
#             小说故事情节曲折，语言生动，人物性格鲜明，具有高度的艺术成就。但作品歌颂、美化宋江，鼓吹“忠义”和“替天行道”，表现出严重的思想局限。
#         '''
#     NewBook.PHOTO = ''
#     NewBook.TYPE = '16'
#     NewBook.PAPERTOTAL = '922'
#     NewBook.WORDTOTAL = '912000'
#     NewBook.SELLSTARTTIME = '2006-03-20'
#     NewBook.SELLENDTIME = '2021-07-12'
#
#     NewBook.save()
#     print('插入成功')
#
# def fun_update_book():
#     try:
#         obj = Book.objects.get(PRODUCTID=1)  #返回结果有且只有一个
#         obj.NAME='水浒'
#         obj.save()
#         print('更新成功')
#     except Book.DoesNotExist:
#         print('PRODUCTID=1的记录不存在，未更新任何数据')




