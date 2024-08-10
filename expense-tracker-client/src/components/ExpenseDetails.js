import React from 'react';

function ExpenseDetails({ expense, onDelete }) {
  return (
    <div>
      <h2>Expense Details</h2>
      <p>ID: {expense.id}</p>
      <p>Name: {expense.name}</p>
      <p>Category: {expense.category}</p>
      <p>Amount: {expense.amount}</p>
      <p>Currency: {expense.currency}</p>
      <p>Tag: {expense.tag}</p>
      <p>Notes: {expense.notes}</p>
      <button onClick={() => onDelete(expense.id)}>Delete</button>
    </div>
  );
}

export default ExpenseDetails;
