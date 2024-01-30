from sqlalchemy import Column, Integer, String, ForeignKey, func
from sqlalchemy.orm import relationship
from sqlalchemy.orm import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from aiogram.types.labeled_price import LabeledPrice


Base = declarative_base()


class Goods(Base):
    __tablename__ = 'goods'
    goods_id = Column(Integer, primary_key=True)
    section = Column(String)
    name = Column(String)
    volume = Column(Integer)
    price = Column(Integer)

    # full description of an item in the menu is generated, i.e. espresso 40 ml, 250R
    # when an instance of the Goods class is referred to
    def __repr__(self):
        return f"""{self.name}{' ' if self.volume > 0 else ''}{self.volume if self.volume > 0 else ''}{' мл' if self.volume > 0 else ''}, {self.price} ₱"""


class Carts(Base):
    __tablename__ = 'carts'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer)
    goods_id = Column(Integer, ForeignKey('goods.goods_id'))
    amount = Column(Integer)
    goods = relationship("Goods")


class Invoices(Base):
    __tablename__ = 'invoices'
    invoice_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer)
    issued_status = Column(Integer)
    payment_status = Column(Integer)


class Invoices_Data (Base):
    __tablename__ = 'invoices_data'
    id = Column(Integer, primary_key=True, autoincrement=True)
    invoice_id = Column(Integer, ForeignKey('invoices.invoice_id'))
    goods_id = Column(Integer, ForeignKey('goods.goods_id'))
    amount = Column(Integer)
    invoices = relationship("Invoices")
    goods = relationship("Goods")


# returns number o items in the cart of a particular user
async def cart_len(u_id):
    query = session.query(Carts).filter_by(user_id=u_id)
    session.commit()
    return query.count()


# adding chosen item to the cart of a particular user
async def cart_add(u_id, g_id):
    session.add(Carts(user_id=u_id, goods_id=g_id, amount=1))
    session.commit()


# all items in the cart of a particular user are deleted
async def cart_empty(u_id):
    session.query(Carts).filter(Carts.user_id == u_id).delete()
    session.commit()


# returns a list of items in the cart (and respective prices) to be invoiced to a particular user
# creates a new invoice for a particular user based on the current goods in the users cart
async def invoice_issue(u_id):
    qry = session.query(Carts).filter_by(user_id=u_id)
    session.commit()
    new_invoice = Invoices(user_id=u_id, issued_status=1, payment_status=0)
    session.add(new_invoice)
    session.commit()
    print(new_invoice.invoice_id)
    prices = []
    for s in qry:
        prices.append(LabeledPrice(label=str(s.goods), amount=s.goods.price * 100))
        session.add(Invoices_Data(invoice_id=new_invoice.invoice_id, goods_id=s.goods.goods_id, amount=1))
    session.commit()
    print(prices)
    # (LabeledPrice(label="Дабл эспрессо, 60 мл", amount=99 * 100)], 321)  # в копейках (руб), номер счёта)
    return (prices, new_invoice.invoice_id)


async def invoice_pay(invoice_id):
    qry1 = session.query(Invoices).filter_by(invoice_id=invoice_id).first()
    if qry1:
        qry1.payment_status = 1
        session.commit()
        qry2 = session.query(Invoices_Data).filter_by(invoice_id=invoice_id)
        session.commit()
        res = {}
        if qry2:
            for line in qry2:
                print(str(line.goods), str(line.amount))
                # res.setdefault(str(line.goods), [line.amount])[-1] += 1
                res.setdefault(str(line.goods), [0])[-1] += 1
            return res





def kb_labels(menu_code):  # m_level
    if menu_code == '0':  # labels for top level menu (e.g. Classic menu, Ice menu, etc.)
        query = session.query(Goods.section).distinct()
        result = [r[0] for r in query]
    elif len(menu_code) == 1:  # labels for the second level menu with names of the drinks (e.g. espresso, cappuccino)
        query = session.query(Goods.name).filter(Goods.goods_id.startswith(menu_code)).distinct()
        print(query[0])
        print(*query)
        result = [r[0] for r in query]
    else:  # labels for third the level menu with full names of the drinks with volume and price  (e.g. espresso 40 ml 80 rub.)
        query = session.query(Goods.name, Goods.volume, Goods.price).filter(
            Goods.goods_id.startswith(menu_code)).distinct()
        result = f"{query[0][0]} {query[0][1] if query[0][1] != 0 else ''}{' мл ' if query[0][1] != 0 else ''}{query[0][2]} ₱"
        print(query[0])
        print(*query)
        # result = query[0]
    return result


# loads menu from db to the Menu.menu_dict dictionary (i.e. the only attribute of the Menu dataclass) on bot startup
# def menu_loader():
#     menu_dict = {}
#     query = session.query(Goods.section).distinct()
#     i_keys = [r[0] for r in query]
#     # print(i_keys)
#     for a in i_keys:
#         menu_dict[a] = {}
#         query = session.query(Goods.name).filter(Goods.section == a).distinct()
#         ii_keys = [r[0] for r in query]
#         # print(ii_keys)
#         for b in ii_keys:
#             menu_dict[a][b] = {}
#             query = session.query(Goods, Goods.goods_id).filter(Goods.name == b).distinct()
#             for c in query:
#                 menu_dict[a][b][str(c[0])] = c[1]
#     # print(menu_dict)
#     return menu_dict

def menu_loader():
    menu_level0 = {}
    query1 = session.query(Goods.section).distinct()
    # print(*query1)
    for s in query1:
        query2 = session.query(Goods.goods_id, Goods.section).filter(Goods.section == s[0]).first()
        # unique menu section names as values and first digits of the ids as keys
        menu_level0[str(query2[0])[0]] = query2[1]
    # print(menu_level0)

    menu_level1 = {}
    query1 = session.query(Goods.name).distinct()
    # print(*query1)
    for s in query1:
        query2 = session.query(Goods.goods_id, Goods.name).filter(Goods.name == s[0]).first()
        # unique goods names as values and three first digits of the ids as keys
        menu_level1[str(query2[0])[:3]] = query2[1]
    print(menu_level1)

    menu_level2 = {}
    query1 = session.query(Goods.goods_id, Goods).all()
    # full goods names as values and full ids as keys
    for s in query1:
        menu_level2[s[0]] = str(s[1])
    # print(menu_level2)
    return [menu_level0, menu_level1, menu_level2]

    # query3 = session.query(Goods.name).distinct()
    #     for s in query1:
    #         query2 = session.query(Goods.goods_id, Goods.name).filter(Goods.name == s[0]).first()
    #         ii_keys.append(f'{str(query2[0])[:3]}_{query2[1]}')
    #     for b in ii_keys:
    #         menu_dict[a][b] = {}
    # print(menu_dict)
    #         query = session.query(Goods, Goods.goods_id).filter(Goods.name == b).distinct()
    #         for c in query:
    #             menu_dict[a][b][str(c[0])] = c[1]
    # print(menu_dict)
    # return menu_dict

# Create an engine and session
engine = create_engine('sqlite:///coffee-10.db')
Session = sessionmaker(bind=engine)
session = Session()

# Create the tables in the database
Base.metadata.create_all(engine)
