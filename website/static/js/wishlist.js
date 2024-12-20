function toggleWishlist(button) {
    const productId = button.getAttribute("data-product-id");
    const heartIcon = button.querySelector("i");

    const isInWishlist = heartIcon.classList.contains("fas");


    const url = isInWishlist ? `/remove_from_wishlist/${productId}` : `/add_to_wishlist/${productId}`;
    
    fetch(url, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === "added") {
            heartIcon.classList.remove("far");
            heartIcon.classList.add("fas");
        } else if (data.status === "removed") {
            heartIcon.classList.remove("fas");
            heartIcon.classList.add("far");
        }
    })
    .catch(error => {
        console.error("Error:", error);
    });
}
