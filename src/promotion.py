import tkinter as tk

def show_promotion_popup():
    # Create the root window (hidden)
    root = tk.Tk()
    root.withdraw()  # Hide the main window (we only want the pop-up)

    # Here, you could show options to promote the pawn
    promote_options = tk.Toplevel(root)  # Create a new popup window
    promote_options.title("Choose Promotion")

    promotion_choice = None  # This variable will hold the promotion choice

    def on_close():
        nonlocal promotion_choice
        promotion_choice = None  # Set promotion_choice to None if window is closed
        promote_options.quit()  # Close the popup
        promote_options.destroy()  # Destroy the popup window

    # Bind the close event (when the X button is clicked)
    promote_options.protocol("WM_DELETE_WINDOW", on_close)

    def promote_to_queen():
        nonlocal promotion_choice
        promotion_choice = "queen"
        promote_options.quit()  # Close the popup
        promote_options.destroy()  # Destroy the popup window

    def promote_to_rook():
        nonlocal promotion_choice
        promotion_choice = "rook"
        promote_options.quit()  # Close the popup
        promote_options.destroy()  # Destroy the popup window

    def promote_to_knight():
        nonlocal promotion_choice
        promotion_choice = "knight"
        promote_options.quit()  # Close the popup
        promote_options.destroy()  # Destroy the popup window

    def promote_to_bishop():
        nonlocal promotion_choice
        promotion_choice = "bishop"
        promote_options.quit()  # Close the popup
        promote_options.destroy()  # Destroy the popup window

    # Create buttons for each promotion choice
    tk.Button(promote_options, text="Queen", command=promote_to_queen).pack(pady=5)
    tk.Button(promote_options, text="Rook", command=promote_to_rook).pack(pady=5)
    tk.Button(promote_options, text="Knight", command=promote_to_knight).pack(pady=5)
    tk.Button(promote_options, text="Bishop", command=promote_to_bishop).pack(pady=5)

    promote_options.mainloop()  # Start the event loop for the popup

    return promotion_choice  # Return the promotion choice as a string or None
