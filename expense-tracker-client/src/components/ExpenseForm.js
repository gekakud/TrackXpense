import React, { useState, useEffect } from 'react';

function ExpenseForm({ onSubmit, expense, clearForm }) {
  const [formData, setFormData] = useState({
    name: '',
    category: '',
    amount: 0,
    currency: '',
    tag: '',
    notes: ''
  });

  useEffect(() => {
    if (expense) {
      setFormData({
        name: expense.name,
        category: expense.category,
        amount: expense.amount,
        currency: expense.currency,
        tag: expense.tag,
        notes: expense.notes
      });
    } else {
      setFormData({
        name: '',
        category: '',
        amount: 0,
        currency: '',
        tag: '',
        notes: ''
      });
    }
  }, [expense]);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit({ ...formData, id: expense ? expense.id : undefined });
    setFormData({
      name: '',
      category: '',
      amount: 0,
      currency: '',
      tag: '',
      notes: ''
    });
    if (clearForm) clearForm();
  };

  return (
    <div>
      <h2>{expense ? 'Update Expense' : 'Add Expense'}</h2>
      <form onSubmit={handleSubmit}>
        <div>
          <label>Name:</label>
          <input type="text" name="name" value={formData.name} onChange={handleChange} />
        </div>
        <div>
          <label>Category:</label>
          <input type="text" name="category" value={formData.category} onChange={handleChange} />
        </div>
        <div>
          <label>Amount:</label>
          <input type="number" name="amount" value={formData.amount} onChange={handleChange} />
        </div>
        <div>
          <label>Currency:</label>
          <input type="text" name="currency" value={formData.currency} onChange={handleChange} />
        </div>
        <div>
          <label>Tag:</label>
          <input type="text" name="tag" value={formData.tag} onChange={handleChange} />
        </div>
        <div>
          <label>Notes:</label>
          <input type="text" name="notes" value={formData.notes} onChange={handleChange} />
        </div>
        <button type="submit">{expense ? 'Update' : 'Add'}</button>
      </form>
    </div>
  );
}

export default ExpenseForm;
