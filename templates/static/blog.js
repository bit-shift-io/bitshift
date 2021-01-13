const MAX_ITEMS = 3;
const url = 'https://bit-shift.blogspot.com/feeds/posts/default';
const content = document.getElementById('news-content');

const blog = fetch('https://api.rss2json.com/v1/api.json?rss_url=' + encodeURI(url))
    .then(response => response.text())
    .then(str => JSON.parse(str).items);

const tweets = new Promise((resolve, rejct) => {
    const configList = {
        "profile": {"screenName": 'bitshiftio'},
        "domId": 'twitterList',
        "maxTweets": 2,
        "enableLinks": true, 
        "showUser": false,
        "showTime": true,
        "showImages": false,
        "lang": 'en',
        "dataOnly": true,
        "customCallback": populateTpl
    };
    twitterFetcher.fetch(configList);
    
    function populateTpl(tweets){
        resolve(tweets);
    }

    setTimeout(() => {
        // if we get here we are probably blocked!
        resolve([]);
    }, 1000);
});

Promise.all([blog, tweets]).then(r => {
    const blogItems = r[0];
    const tweetItems = r[1];

    // merge results
    const mappedBlogItems = blogItems.map(item => {
        return {
            date: moment(item.pubDate),
            link: item.link,
            title: item.title,
            type: 'blog'
        };
    });

    const mappedTweetItems = tweetItems.map(item => {
        return {
            date: moment(item.time),
            link: item.permalinkURL,
            title: item.tweet,
            type: 'tweet'
        };
    });

    const mappedItems = mappedBlogItems.concat(mappedTweetItems);
    const sortedItems = mappedItems.sort((a, b) => {
        return b.date - a.date;
    });

    const slicedItems = sortedItems.slice(0, MAX_ITEMS);
    return slicedItems;
})
.then(items => {
    const itemsContainer = document.createElement('DIV');
    content.appendChild(itemsContainer);

    for (const item of items) {
        const itemContainer = document.createElement('DIV');
        itemContainer.className = item.type;

        const itemDateElement = document.createElement('DIV');
        itemDateElement.className = 'date';
        const dateString = item.date.format('YYYY-MM-DD');
        itemDateElement.innerText = dateString;

        const itemLinkElement = document.createElement('A');
        itemLinkElement.className = 'title';
        itemLinkElement.setAttribute('href' , item.link);
        itemLinkElement.setAttribute('target' , '_blank');
        itemLinkElement.innerHTML = item.title;

        itemContainer.appendChild(itemLinkElement);
        itemContainer.appendChild(itemDateElement);

        itemsContainer.appendChild(itemContainer);
    }
});
