# ㄒ卄🝗 尸讠㇄㇄闩尺 爪🝗𝓝

The Official Speedwagon Foundation Shop is a simple e-commerce application created for the Secure Web Development block course at Saarland University (ST20).
The project involved development of specific functionalities of a web application, split into 5 parts. 
The description of each part of the project contained a small back story to provide some context for the functionality. 

## Part 1 (Login & Registration)
You have just been hired by a company developing web applications for other businesses. Recently,
a new client has contacted your employer and asked for a new e-commerce application where they
can sell some of their futuristic products. Right now, the client has been very vague about the web
app specifications... but what is for sure is that they do not want anonymous users purchasing
products on their website, but rather, they prefer keeping records of shopping history and of each
user. Since you are the newbie and that there is not so much time pressure, they ask you to start
working on this project by implementing the user management part of the e-commerce application.

Your older colleagues already did some modeling work for you, and these are the specifications that
they give you. The e-commerce web app (let us call it thin air LTD ) needs to have a home page or
landing page reachable at https://thin-air.appsec.saarland/accounts. From here, the user
can either log in, or register; if they already have an active session, we can momentarily show a
welcome message followed by their username.

- By clicking on the login button, the user is redirected to another URL (https://thin-air.appsec.saarland/accounts/login) where they can log in. They will enter their username, password and confirm with a submit button.
-  By clicking on the registration button, the user is again redirected to a third URL (https://thin-air.appsec.saarland/accounts/registration). Here, they just provide their email address (used as username), first and last name, and password.

As this is not much work, they asked you to provide a simple user interface that you can show to
the client during the next meeting, to show a couple of features and ask for feedback. Of course, this
means that the website has to be fully functional, and you need to be able to register actual users
(even if dummy ones) and show the client that data is stored in the back-end database. Moreover,
you would like to leave a good impression on your colleagues, and implement these services by
paying attention to the security features (e.g., by doing a two-step registration phase).

## Part 2 (Password Reset & Single Sign-On
You managed to develop everything on time, and the representative from thin air LTD was quite
satisfied. Still, as every good businessperson, they asked for an additional functionality to allow
them to expand their potential customer base even further. This time, they want to implement a
Single Sign-On functionality, so that lazy customers are not discouraged by all the typing needed
during the registration procedure, and can just click on the Google "Sign In" button.

Moreover, your colleagues were helping you out and they noticed a missing functionality. They
pointed out that users often forget their passwords – and now you also have to implement a password
recovery function. You know that there are plenty of mechanisms to do so, but your seniors still
want to test your capabilities and do not give you any hint on which one would be better: you need
to consider each of them and decide base on your assessment. You decide to add the password
recovery functionality in the login page.

## Part 3 (API)
Finally, it's the moment to talk business. thin air LTD plans to invest a lot of money in expanding
their platform, and they have something quite complex in mind. To mimic their biggest competitor
(notably e-bay) and try to attract more customers, they want to introduce their own idea of a
marketplace. Long story short, on https://thin-air.appsec.saarland it will be possible to both
buy and sell products. Registered users can buy products sold either from other users, or from
thin air LTD themselves, or from partner business (hereinafter "partners"). This means that your
e-commerce application now needs a second part in charge of managing the shop (products, orders,
payments, and so on).

This is quite a lot to do. You are struggling with planning the implementation of the new features,
and your colleagues give you the following tip: they heard that thin air LTD is struggling with
partner businesses, who are actually also the investors of this project, and thus advise you to
prioritize the "business to business" part of the application. This way, your next deliverable could
help the company representative keeping the stakeholders at bay, and you could also be praised for
your work. You accept, and now have to implement yet another part of the application...
In a first step, https://thin-air.appsec.saarland will issue an API key token to a requesting
partner (a strictly confidential information!). This token will then authorize partners invoking APIs
to either insert products from their shop, or delete products that they previously advertised and
are now not available anymore. By using the token, partners can also retrieve the list of products
registered in the marketplace, and the associated meta-information (e.g., if the price is currently
discounted due to a promotional campaign); part of this information can then be used by Partners
to advertise our products in their websites. These operations are security-sensitive and reveal
confidential data, and thus only the HTTP requests that present a valid API key are authorized.
There is no user interface required, as these services are not intended for physical users browsing
the web site.

Since you managed to implement the SSO and password reset by yourself, your colleagues now
entrust you with the implementation of this API key/access token to authorize requests from
partners. Again, you must consider different possibilities, and decide which one of these best suits
your setting. You need to rise the ranks the hard way...

## Part 4 (Purchasing products)
You now have to implement the user-dedicated part of the e-commerce application. This means
that additionally to the routines that provide the services, you need to take care of HTML pages as
well as database bindings. After meeting with your client and your colleagues, you were able to
draft a specification as follows.

The shopping area of https://thin-air.appsec.saarland is accessible to all users (logged
in and non-logged-in users). The marketplace has a homepage which is accessible under
https://thin-air.appsec.saarland/shop/products/list: here, all products are listed, from
any seller. To make the user interface more compact and clean, not all the product details are
shown, although all details are sent from the server to the client: the user can see them by clicking
on the chosen product, which will open up a HTML DIV panel over the list; this will be handled
in the client-side, without reloading the page. As asked by thin air LTD, each product must
have a unique URL with all the details that people can share. Your seniors have asked you to
reuse the same product list page and the HTML DIV panel for showing the product details, by
storing the data that you need to show in the product panel in the URL hash fragment part (i.e.,
/shop/products/list#<product-details>).
  
Users can add or remove products from their cart by using specific buttons, each couple paired with
its product in the list web page. Each product in the list has an "Add to Basket" button. When this
button is clicked by a non-logged user, they are redirected to the login page, and after a successful
login, the selected product will be added to their basket subject to its availability. For logged user,
the selected product will be added to the basket upon clicking on the "Add to Basket" button
depending on its availability. The total amount due for the shopping is shown in the top left corner
of the page, and it automatically updates when items are added or removed; cart details (items,
amount, price, ...) are shown at https://thin-air.appsec.saarland/shop/products/basket/.
  
Users with an ongoing order can proceed to the checkout page, by clicking on the checkout button
at anytime. Here, they are asked to provide an address (at the moment, it is not relevant whether
shipping and billing address are separated) and to choose a method of payment between the
supported ones. If the data they provided is valid and correct, the address and payment information
are finalized in the database, the cart is emptied and the order marked as placed, and – of course –
money is automatically withdrawn from the provided payment endpoint. You noted down a comment
from your client: he once had a startup (before it went bankrupt) where users managed to buy too
many items of the same product, while actually it was unavailable! Somehow, they were seeing
inconsistent views... and the refund process was a terrible headache.
  
The good news is that you can reuse part of the model that you already implemented (for partners
and products); the bad news, well...

## Part 5 (Private & Public Profile Web Page)
 The e-commerce website for thin air LTD seems to be finished, and you are waiting for the final
response from your boss, who should come any minute now from the meeting with the company
representative.
  
You meet with her and get to know that the client was not completely satisfied, due to a feature
missing in the prototype: there was no page where the client could see a user's personal details,
or order history for example. You try to reassure your boss by telling him that you were already
working on this feature, but have not presented it yet, due to a specific concern. In fact, you
were recently at a security conference, where you heard of how users of certain websites can be
de-anonymized, or have personal information leaked.
  
As your boss is not entirely convinced (and now your colleagues know of this as well), you ought
to implement this properly. The client requested a user profile page containing the user's private
information. Additionally, the client came up with a new requirement, i.e., a public "store front"
for every user who also sells products. Thus, users of the ecommerce web application can now
sell products in their publicly available "store front". To estimate how often these pages are
viewed, the client has asked you to use the Google Analytics tag (i.e., the Google's analytics.js
library). The client owns another ecommerce web applications too, known as high-air (i.e.,
https://example.high-air.com), and they want us to identify the returning customers between
the two applications leveraging the Google Analytics tag. Thus, you are asked to enable cross-domain
tracking of users (i.e., between the domain of your application, thin-air, and the domain of the
client's second ecommerce web application, high-air).
  
As these are both functionalities intended for the end user, you not only have to implement the
routines providing the service, but also the corresponding HTML pages. After thinking it through,
you realize that, in fact, these use-cases are subject to potential information leakage (as other users
could, purposefully or accidentally, exfiltrate information from there), so you probably have to read
that research work again and find out how to avoid that happening.

## Final Remarks
#### *Is This a JoJo Reference?*
