var row_id = null;
var order_table_id = "item_table";
var product_table_id = "dataTable";

if (document.getElementById(order_table_id) !== null) {
    row_id = document.getElementById(order_table_id).rows.length;
} else if (document.getElementById(product_table_id) !== null) {
    row_id = document.getElementById(product_table_id).rows.length;
}


console.log(row_id);


function addFilter() {
    // get the index of the last filter row
    const filterRows = document.querySelectorAll('.filter-form');
    const lastIndex = filterRows.length - 1;

    // clone the last filter row and update the index
    const lastRow = filterRows[lastIndex];
    const newRow = lastRow.cloneNode(true);
    const newIndex = lastIndex + 1;

    // update the IDs and names of the cloned row's form elements
    const idRegex = /-\d+/;
    const nameRegex = /_\d+/;
    newRow.id = newRow.id.replace(idRegex, `-${newIndex}`);
    Array.from(newRow.querySelectorAll('[id]')).forEach(el => {
        el.id = el.id.replace(idRegex, `-${newIndex}`);
    });
    Array.from(newRow.querySelectorAll('[name]')).forEach(el => {
        el.name = el.name.replace(nameRegex, `_${newIndex}`);
    });

    // add the cloned row after the last filter row
    lastRow.parentNode.insertBefore(newRow, lastRow.nextSibling);
}


$(document).ready(function () {

//add row
    $('.item_bar').focus();


//remove row
    $(document).on('click', '.remove', function () {
        $(this).closest('tr').remove();
        totalamount();
        console.log("Inside function remove")
    });

    //autocomplete set to 'on' if input value is greater than or equal to 3
    $(document).ready(function () {
        $('.autocomplete').on('input', function () {
            autocompleteFunction(this.value);
        });
    });

    function autocompleteFunction(value) {
        const inputField = document.querySelector('.autocomplete');
        if (value.length >= 3) {
            inputField.setAttribute('autocomplete', 'on');
        } else {
            inputField.setAttribute('autocomplete', 'off');
        }
    }


//prevent enter to work on the page
    $(document).keypress(function (event) {
        if (event.which === '13') {
            event.preventDefault();
        }
    });

//insert data to database
    $('#insert_form').on('submit', function (event) {
        event.preventDefault();
        var error = '';
        $('.item_bar').each(function () {
            var count = 1;
            if ($(this).val() === '') {
                error += "<p>Enter Item Name at " + count + " Row</p>";
                return false;
            }
            count = count + 1;
        });

        $('.item_quantity').each(function () {
            var count = 1;
            if ($(this).val() === '') {
                error += "<p>Enter Item Quantity at " + count + " Row</p>";
                return false;
            }
            count = count + 1;
        });


        if (error === '') {
            $.ajax({
                url: "/insert",
                method: "POST",
                data: $(this).serialize(),
                success: function (data) {
                    if (data.data === 'ok') {
                        $('#item_table').find("input").val('');
                        $('#item_table').find("tr:gt(1)").remove();
                        $('#total_amount').val('');
                        row_id = 2;
                        $('#error').html('<div class="alert alert-success">Item Details Saved</div>');
                    }
                }
            });
        } else {
            $('#error').html('<div class="alert alert-danger">' + error + '</div>');
        }
    });

});


$('#supplier-form').on('submit', function (event) {
    console.log("inside")
    // alert("this")
    event.preventDefault();
    $.ajax({
        type: "POST",
        url: "/suppliers",
        data: $('#supplier-form').serialize(),
        success: function (response) {
            // If the server returns a success message, close the modal and reload the page
            if (response.success) {
                console.log("success")
                $('#exampleModal').modal('hide');
                location.reload();
            } else {
                // If the server returns an error message, display it inside the modal
                $('.modal-body #supplier-form').prepend('<div class="alert alert-danger">' + response.error + '</div>');
                console.log("not success")

            }
        },
        error: function (response) {
            // If the server returns an error, display an error message inside the modal
            $('#supplier-form .modal-body').prepend('<div class="alert alert-danger">An error occurred...</div>');
        }
    });
});

// Product: Pass the selected supplier's id and name from the form-control back to Flask
$('#exampleInput4').change(function () {
    var supplierName = $('#exampleInput4 option:selected').text();
    console.log(supplierName)
    $('#supplierName').val(supplierName);
});


//// Product: initialize the multiselect plugin
//$(document).ready(function() {
//    $('.bootstrap-multiselect').multiselect();
//});

// Product: Run filter to filter table display in product 02/04/2023
$(document).ready(function () {
    $('#filter-form').on('submit', function (event) {
        console.log("In #filter-form");
        var supplierName = $('#filter-form option:selected').text();
        console.log(supplierName);
        $('#selectedSupplier').val(supplierName);
        // // Product: Pass the selected supplier's id and name from the form-control back to Flask
        // event.preventDefault();
        // var supplierId = $('#supplier-select').val();
        // $('tbody tr').show();
        // if (supplierId) {
        //     $('tbody tr').not('[data-supplier-id="' + supplierId + '"]').hide();
        // }
    });
});

// Filter icon section 02/04/2023
$(document).ready(function () {
    // $('.filter-icon').click(function() {
    //     $(this).siblings('.filter-form').toggle();
    // });

    $(document).ready(function () {
        $('.filter-icon').click(function () {
            $('.filter-container').toggleClass('d-none');
        });
    });

    // add new filter-form when the "Add filter +" button is clicked
// select the button and attach a click event listener
    $('.add-filter-btn').click(function () {
        // get the filter container element
        var filterContainer = $(this).closest('.filter-container');

        // add the new filter form
        addFilter(filterContainer);

        // retrieve the data from the session
        var data = JSON.parse('{{ session["data"]|default("[]") }}');

        // create a new filter object and add it to the data
        var filter = {
            'column': '',
            'condition': '',
            'value': ''
        };
        data.push(filter);

        // store the updated data in the session
        $.ajax({
            url: '/store_data',
            type: 'GET',
            data: {value: data},
            success: function (response) {
                console.log(response);
            },
            error: function (error) {
                console.log(error);
            }
        });
    });
});

$(document).ready(function () {
    // load filters from the server
    $.ajax({
        url: '/retrieve_data',
        type: 'GET',
        success: function (data) {
            // loop through the filters and fill in the form fields
            for (var i = 0; i < data.filters.length; i++) {
                var filter = data.filters[i];
                var filterForm = $('.filter-form').eq(i);
                filterForm.find('.filter-column').val(filter.column);
                filterForm.find('.filter-condition').val(filter.condition);
                filterForm.find('.filter-value').val(filter.value);
            }
        },
        error: function (error) {
            console.log(error);
        }
    });
});


// save the chosen filters when the "Save changes" button is clicked
// $('.save-changes-btn').click(function () {
$('#filter-property-form').on('submit', function (event) {
    var filters = [];
    $('.filter-container').find('.filter-form').each(function () {
        var column = $(this).find('.filter-column').val();
        var condition = $(this).find('.filter-condition').val();
        var value = $(this).find('.filter-value').val();
        if (column && condition && value) {
            filters.push({
                'column': column,
                'condition': condition,
                'value': value
            });
        }
    });
    console.log(filters)
    // $('#filterQuery').val(filters);
    // $.ajax({
    //     type: 'GET',
    //     url: '/products',
    //     data: {'filters': JSON.stringify(filters)},
    //     success: function(response) {
    //         // do something with the response from the server
    //         console.log("Done")
    //     }
    // });
});

$(document).ready(function() {
    $('.select2').select2();
});
// clear all filters when the "x Clear all" button is clicked
$('.clear-all-btn').click(function () {
    $('.filter-form').not(':first').remove();
    $('.filter-form:first').find('.filter-column, .filter-condition, .filter-value').val('');
});


// function addrow() {
//   var html = '';
//
//   html += '<tbody>';
//   html += '<tr>';
//     html += '<td><input type="text" name="item_name[]" class="form-control item_name" id ="name_'+row_id+'" readonly/></td>';
//     html += '<td><input type="text" name="item_bar[]" class="form-control item_bar" id ="item_'+row_id+'" onkeydown="getProduct(event,'+row_id+');"/></td>';
//     html += '<td><input type="text" name="item_quantity[]" class="form-control item_quantity" id="qty_'+row_id+'" onkeyup="getTotal(row_id)"/></td>';
//   html += '<td><input type="text" name="price[]" class="form-control item_price" id ="price_'+row_id+'" readonly /></td>';
//   html += '<td><input type="text" name="total[]" class="form-control item_total" id ="total_'+row_id+'" readonly /></td>';
//   html += '<td><button type="button" name="remove" class="btn btn-danger btn-sm remove"><i class="fas fa-minus"></i></button></td></tbody></tr>';
//   $('#item_table').append(html);
//   $('.item_bar').focus();
//   row_id += 1 ;
// }


function addrow() {
    var html = '';
    var row_id = $("#item_table tbody tr:last-child").index() + 2;

   $.ajax({
        url: '/get_products',
        type: 'GET',
        success: function(data) {
            html += '<tbody>';
            html += '<tr>';
            html += '<td>';
            html += '<select name="product_name[]" class="form-control item_name" id ="name_' + row_id + '" onchange="updateRow(' + row_id + ')">';
            html += '<option value="">Select Product</option>';
            for (var i = 0; i < data.length; i++) {
                html += '<option value="' + data[i].id + '" data-price="' + data[i].price + '"" data-barcode="' + data[i].barcode + '">' + data[i].name + '</option>';
            }
            html += '</select>';
            html += '</td>';
            html += '<td><input type="text" name="item_bar[]" class="form-control item_bar" id ="item_' + row_id + '" readonly/></td>';
            html += '<td><input type="text" name="item_quantity[]" class="form-control item_quantity" id ="qty_' + row_id + '" onkeyup="getTotal(' + row_id + ')"/></td>';
            html += '<td><input type="text" name="price[]" class="form-control item_price" id ="price_' + row_id + '" value="" readonly /></td>';
            html += '<td><input type="text" name="total[]" class="form-control item_total" id ="total_' + row_id + '" readonly /></td>';
            html += '<td><button type="button" name="remove" class="btn btn-danger btn-sm remove" id="remove_' + row_id + '"><i class="fas fa-minus"></i></button></td></tbody></tr>';
            $('#item_table').append(html);
            $('.item_bar').focus();
        },
        error: function(xhr, status, error) {
            console.log(error);
        }
    });
}


function getTotal(row_id) {
    var q = $("#qty_" + row_id).val();
    var p = $("#price_" + row_id).val();
    $("#total_" + row_id).val(q * p);
    totalamount();
}

function updatePrice(row_id) {
    var select = document.getElementById('name_' + row_id);
    var priceInput = document.getElementById('price_' + row_id);
    var selectedOption = select.options[select.selectedIndex];
    var price = selectedOption.getAttribute('data-price');
    priceInput.value = price;
}

function updateBarCode(row_id) {
    var select = document.getElementById('name_' + row_id);
    var barcodeInput = document.getElementById('item_' + row_id);
    var selectedOption = select.options[select.selectedIndex];
    var barcode = selectedOption.getAttribute('data-barcode');
    barcodeInput.value = barcode;
}

function updateRow(row_id) {
    updatePrice(row_id);
    updateBarCode(row_id);
}



function getProduct(event, row_id) {
    if (event.which === 13) {
        var item_bar = $('#item_' + row_id).val();
        var values = $("input[name='item_bar[]']").map(function () {
            return $(this).val();
        }).get();
        //this will check if the same value is enterd then do not enter it to the table instead increment the Quantity by one .. we did not take the last element becuse it will be the same

        for (var i = 0; i < values.slice(0, -1).length; i++) {
            if (item_bar == values[i]) {
                var n = Number($('#item_table').find("#qty_" + (i + 1)).val());
                $('#item_table').find("#qty_" + (i + 1)).val((n + 1))
                getTotal(i + 1);
                $('#item_' + row_id).val('');
                totalamount();
                // this is to get out of the function
                return;
            }
        }

        $.ajax({
            url: '/data',
            contentType: 'application/json;charset=UTF-8',
            type: 'POST',
            data: JSON.stringify(item_bar),
            success: function (response) {
                if (response.quantity === 0) {
                    alert("sorry you do not have enough product")
                } else {
                    $("#price_" + row_id).val(response.price);
                    $("#name_" + row_id).val(response.name);
                    $("#qty_" + row_id).val(1);
                    getTotal(row_id);
                    totalamount();
                    addrow();
                }

            },
            error: function (error) {
                // console.log(error);
                alert("sorry you do not have this product")
            }
        });


    }
}

function totalamount() {
    var total = 0;
    $('.item_total').each(function () {
        var i = Number($(this).val());
        total += i;
        // total += parseFloat($(this).val());
    });

    $('#total_amount').val(total);

}



