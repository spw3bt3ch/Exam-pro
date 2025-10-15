## **Get Access Token**
Create a free account at https://questions.aloc.com.ng  On your dashboard, retrieve Access Token that will be attached to each API call.

A sample Access Token should look like this `ALOC-78bfe77b49fb3e407bf8`

## A sample code


    fetch('https://questions.aloc.com.ng/api/v2/q?subject=chemistry', {
      headers: {
        Accept: 'application/json',
        'Content-Type': 'application/json',
        AccessToken: 'ALOC-78bfe77b49fb3e407bf8',
      },
      method: 'GET',
    })
      .then(response => response.json())
      .then(data => {
        console.log('data', data);
      })
      .catch(error => {
        console.log('error', error);
      });

## Complete example
  
![A full example](https://res.cloudinary.com/aloc-ng/image/upload/v1687019937/ALOC-Questions/Screenshot_2023-06-17_at_17.36.03_adncfs.png)


## API Response sample

Get a question

https://questions.aloc.com.ng/api/v2/q?subject=chemistry

![Sample response](https://camo.githubusercontent.com/bbd478af798a9635fd29974fb55d1b8b2170e70f7f891bec075d7950204f26cc/68747470733a2f2f616c6f632e636f6d2e6e672f61737365742f696d616765732f6f74686572732f616c6f632d6170692d73616d706c652e706e67)

## **Post APIs Doc**

https://documenter.getpostman.com/view/1319216/2s9YCBuA3V

## **API call Examples**

**NOTE: Always add Access Token as shown above in each API call** 


https://questions.aloc.com.ng/api/v2/q?subject=chemistry

Get many questions (returns 40 by default)

https://questions.aloc.com.ng/api/v2/m?subject=chemistry

Get many questions (limit 120)

https://questions.aloc.com.ng/api/v2/m/100?subject=chemistry

Get several questions (limit 40)

https://questions.aloc.com.ng/api/v2/q/7?subject=chemistry

https://questions.aloc.com.ng/api/v2/q/25?subject=chemistry

Get a question by year

https://questions.aloc.com.ng/api/v2/q?subject=chemistry&year=2005

Get a question by exam type

https://questions.aloc.com.ng/api/v2/q?subject=chemistry&type=utme

Get a question by type and year

https://questions.aloc.com.ng/api/v2/q?subject=chemistry&year=2010&type=utme

Get question by id and subject

https://questions.aloc.com.ng/api/v2/q-by-id/1?subject=chemistry

For more detailed examples visit https://questions.aloc.com.ng