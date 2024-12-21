$('.plus-cart').click(function(){
    console.log('Button clicked')

    var id = $(this).attr('pid').toString()
    var quantity = this.parentNode.children[2]

    $.ajax({
        type: 'GET',
        url: '/pluscart',
        data: {
            cart_id: id
        },
        
        success: function(data){
            console.log(data)
            quantity.innerText = data.quantity
            document.getElementById(`quantity${id}`).innerText = data.quantity
            document.getElementById('amount_tt').innerText = data.amount
            document.getElementById('totalamount').innerText = data.total

        }
    })
})


$('.minus-cart').click(function(){
    console.log('Button clicked')

    var id = $(this).attr('pid').toString()
    var quantity = this.parentNode.children[2]

    $.ajax({
        type: 'GET',
        url: '/minuscart',
        data: {
            cart_id: id
        },
        
        success: function(data){
            console.log(data)
            quantity.innerText = data.quantity
            document.getElementById(`quantity${id}`).innerText = data.quantity
            document.getElementById('amount_tt').innerText = data.amount
            document.getElementById('totalamount').innerText = data.total

        }
    })
})


$('.remove-cart').on('click', function(e){
    e.preventDefault(); 
    console.log("Button clicked"); 
    var id = $(this).attr('pid').toString(); 
    var to_remove = $(this).closest('.product-item');

    $.ajax({
        type: 'GET',
        url: '/removecart',
        data: {
            cart_id: id
        },
        success: function(data){
            console.log(data); 
            $('#amount_tt').text(data.amount);
            $('#totalamount').text(data.total);

            to_remove.fadeOut(500, function() {
                $(this).remove();  
            });
        },
        error: function(xhr, status, error) {
            console.error("Error removing item from cart: " + error);
        }
    });
});


