/**
 * Created by Overdese
 */

function addPostPreview(post, row_id){
    var postHtml = '<div class="col-md-4 row-bottom">' +
                   '<div class="text-on-img">' +
                   '<a href="' + post.url + '" class="link-img"><img src="' + post.image + '" class="img-rounded" width="100%">' +
                   '<span class="img-text">' + post.title +'</span></a>' +
                   '</div></div>';
    $('#row_posts_'+row_id).append(postHtml)
}


function postsUpdate(url, count){        
    $.ajax({
        url: url,
        method: 'GET',
        beforeSend: function(){
            $('#btn_more_posts').button('loading')
        },
        dataType: 'json',
        complete: function(jqXHR){
            switch (jqXHR.status) {
                case 200:
                    var items = jqXHR.responseJSON['posts'];
                    var row_id = Number($('#show_posts').attr('data-last-row-id'));
                    $('#show_posts').attr('data-last-count', count)
                    var col_id = $('#row_posts_'+row_id).attr('data-last-col-id');

                    if (typeof col_id == 'undefined') {
                        col_id = 0
                    } else {
                        col_id = Number(col_id)
                    }
                    items.forEach(function(item){
                        if (col_id == 0){
                            var posts_div = $('#show_posts');
                            posts_div.attr('data-last-row-id', row_id);
                            posts_div.append('<div class="row " id="row_posts_'+row_id+'" data-last-col-id="0">');

                        }

                        addPostPreview(item, row_id);

                        col_id += 1;

                        if (col_id == 3) {
                            col_id = 0;
                            row_id += 1;
                            $('#show_posts').attr('data-last-row-id', row_id)
                        } else {
                            $('#row_posts_'+row_id).attr('data-last-col-id', col_id);
                        }
                    });
                    $('#btn_more_posts').button('reset')
                    break;
                default:
                    $('#btn_more_posts').button('reset')
                    break;
            }        
        }

    });        
}
