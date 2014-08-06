// ==UserScript==
// @name        youtube-mpd
// @namespace   hrubi@inkorekt.cz
// @description Forwards youtube link to another site
// @include     /https?://(.*\.)?youtube.com/.*/
// @version     1
// @grant       GM_xmlhttpRequest
// @require     https://raw.githubusercontent.com/hrubi/ytmpd/master/client/jquery.min.js
// @require     https://github.com/hrubi/ytmpd/raw/master/client/jquery.noty.packaged.min.js
// ==/UserScript==


var links = document.getElementsByTagName('a');
for ( var i = 0; i < links.length; i++ ) {
    var linkNode = links[i];

    if ( linkNode.href && linkNode.href.match('/watch\\?v=') ) {
        createLink(linkNode, 'add');
    }
}

function addSong(linkNode) {
    var url = linkNode.href,
        title = linkNode.text;
    var n = noty({
        layout: 'bottom',
        type: 'information',
        text: 'Adding song "' + title + '" <img src="http://storage.hrubi.cz/p/img/ajax-loader.gif" />'
    });
    var req = {
        'url': url,
        'title': title
    };
    GM_xmlhttpRequest({
        method: 'POST',
        url: 'http://pirat/play',
        headers: {
            "Content-Type": "application/json"
        },
        data: JSON.stringify(req),
        onload: function(r) {
            try {
                var response = JSON.parse(r.response);
            } catch (err) {
                n.setType('error');
                n.setText('Parsing error: "' + r.response + '"');
                return;
            }
            if (r.status == 200) {
                n.setType('success');
                n.setText(response.text +
                    '<br /><a href="http://pirat/mpd" target="_blank">Go to music player</a>');
                n.setTimeout(5000);
            } else {
                n.setType('error');
                n.setText(response.text);
            }
        }
    });
}

function createLink(linkNode) {
    var addLink = document.createElement('a');
    addLink.addEventListener('click', function() {
        addSong(linkNode);
    });
    addLink.appendChild(document.createTextNode('[MPD]'));
    linkNode.parentNode.insertBefore(addLink, linkNode.nextSibling);
}
