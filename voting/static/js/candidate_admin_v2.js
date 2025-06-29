django.jQuery(function($) {
    console.log('Candidate admin JS v2 loaded');
    
    function updateConstituencies() {
        var countyId = $('#id_county').val();
        var constituencySelect = $('#id_constituency');
        var wardSelect = $('#id_ward');
        
        console.log('updateConstituencies called with countyId:', countyId);
        
        // Clear ward options
        wardSelect.empty();
        wardSelect.append($('<option></option>').attr('value', '').text('---------'));
        
        if (countyId) {
            // Fetch constituencies for the selected county
            console.log('Fetching constituencies for county:', countyId);
            $.getJSON('/load-constituencies/', {county: countyId}, function(data) {
                console.log('Constituencies data received:', data);
                constituencySelect.empty();
                constituencySelect.append($('<option></option>').attr('value', '').text('---------'));
                $.each(data, function(index, item) {
                    constituencySelect.append(
                        $('<option></option>').attr('value', item.id).text(item.name)
                    );
                });
                // Log after updating options
                console.log('Constituency options updated:', constituencySelect.html());
                // Ensure Select2 updates the dropdown
                if (constituencySelect.hasClass('select2-hidden-accessible')) {
                    constituencySelect.trigger('change.select2');
                }
            }).fail(function(xhr, status, error) {
                console.error('Error fetching constituencies:', error);
                console.error('Status:', status);
                console.error('Response:', xhr.responseText);
            });
        } else {
            // Clear constituency options if no county is selected
            console.log('No county selected, clearing constituencies');
            constituencySelect.empty();
            constituencySelect.append($('<option></option>').attr('value', '').text('---------'));
        }
    }

    function updateWards() {
        var constituencyId = $('#id_constituency').val();
        var wardSelect = $('#id_ward');
        
        console.log('updateWards called with constituencyId:', constituencyId);
        
        if (constituencyId) {
            // Fetch wards for the selected constituency
            console.log('Fetching wards for constituency:', constituencyId);
            $.getJSON('/load-wards/', {constituency: constituencyId}, function(data) {
                console.log('Wards data received:', data);
                wardSelect.empty();
                wardSelect.append($('<option></option>').attr('value', '').text('---------'));
                $.each(data, function(index, item) {
                    wardSelect.append(
                        $('<option></option>').attr('value', item.id).text(item.name)
                    );
                });
            }).fail(function(xhr, status, error) {
                console.error('Error fetching wards:', error);
                console.error('Status:', status);
                console.error('Response:', xhr.responseText);
            });
        } else {
            // Clear ward options if no constituency is selected
            console.log('No constituency selected, clearing wards');
            wardSelect.empty();
            wardSelect.append($('<option></option>').attr('value', '').text('---------'));
        }
    }

    // Bind the change events
    $('#id_county').on('change', function() {
        console.log('County changed to:', $(this).val());
        updateConstituencies();
    });
    $('#id_constituency').on('change', function() {
        console.log('Constituency changed to:', $(this).val());
        updateWards();
    });

    // Initial load
    console.log('Initial load - calling updateConstituencies and updateWards');
    updateConstituencies();
    updateWards();
}); 