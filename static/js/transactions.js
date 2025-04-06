document.addEventListener('DOMContentLoaded', function() {
    // For the add/edit transaction form
    const transactionTypeRadios = document.querySelectorAll('input[name="transaction_type"]');
    const categorySelect = document.getElementById('category_id');
    
    if (transactionTypeRadios.length && categorySelect) {
        // Function to update categories based on selected type
        function updateCategories(type) {
            // Clear existing options
            categorySelect.innerHTML = '<option value="">Select a category</option>';
            
            // Fetch categories by type
            fetch(`/api/categories/${type}`)
                .then(response => response.json())
                .then(categories => {
                    categories.forEach(category => {
                        const option = document.createElement('option');
                        option.value = category.id;
                        option.textContent = category.name;
                        categorySelect.appendChild(option);
                    });
                    
                    // If this is an edit form and we have a preset value, select it
                    const preSelectedCategory = categorySelect.dataset.preselected;
                    if (preSelectedCategory) {
                        categorySelect.value = preSelectedCategory;
                    }
                })
                .catch(error => console.error('Error fetching categories:', error));
        }
        
        // Initial population based on default selection
        const checkedRadio = document.querySelector('input[name="transaction_type"]:checked');
        if (checkedRadio) {
            updateCategories(checkedRadio.value);
        } else {
            // If no radio is checked, default to expense
            document.getElementById('type_expense').checked = true;
            updateCategories('expense');
        }
        
        // Update categories when transaction type changes
        transactionTypeRadios.forEach(radio => {
            radio.addEventListener('change', function() {
                updateCategories(this.value);
            });
        });
    }
    
    // For transaction list filtering
    const dateRangeToggle = document.getElementById('dateRangeToggle');
    const dateRangeFields = document.getElementById('dateRangeFields');
    
    if (dateRangeToggle && dateRangeFields) {
        dateRangeToggle.addEventListener('change', function() {
            dateRangeFields.style.display = this.checked ? 'block' : 'none';
            
            // Clear date fields if toggle is turned off
            if (!this.checked) {
                document.getElementById('start_date').value = '';
                document.getElementById('end_date').value = '';
            }
        });
        
        // Initialize based on initial state
        dateRangeFields.style.display = dateRangeToggle.checked ? 'block' : 'none';
    }
    
    // Delete transaction confirmation
    const deleteButtons = document.querySelectorAll('.delete-transaction');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to delete this transaction? This action cannot be undone.')) {
                e.preventDefault();
            }
        });
    });
});
