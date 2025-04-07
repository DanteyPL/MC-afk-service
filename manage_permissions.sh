#!/bin/bash

# Database connection parameters
DB_HOST="localhost"
DB_PORT="5432"
DB_NAME="afk_client"
DB_USER="postgres"
DB_PASSWORD="postgres"

# Check if psql is installed
if ! command -v psql &> /dev/null
then
    echo "PostgreSQL client (psql) is not installed. Please install it first."
    exit 1
fi

# Function to add to whitelist
whitelist_player() {
    local ign=$1
    echo "Adding $ign to whitelist..."
    PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -c \
        "INSERT INTO whitelist (ign, approved) VALUES ('$ign', true) ON CONFLICT (ign) DO UPDATE SET approved = true;"
}

# Function to remove from whitelist
remove_from_whitelist() {
    local ign=$1
    echo "Removing $ign from whitelist..."
    PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -c \
        "DELETE FROM whitelist WHERE ign = '$ign';"
}

# Function to grant admin permissions
grant_admin() {
    local email=$1
    echo "Granting admin privileges to $email..."
    PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -c \
        "UPDATE users SET is_admin = true WHERE email = '$email';"
}

# Function to revoke admin permissions
revoke_admin() {
    local email=$1
    echo "Revoking admin privileges from $email..."
    PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -c \
        "UPDATE users SET is_admin = false WHERE email = '$email';"
}

# Main menu
while true; do
    echo ""
    echo "Minecraft AFK Client Permission Manager"
    echo "1. Whitelist player"
    echo "2. Remove player from whitelist"
    echo "3. Grant admin privileges"
    echo "4. Revoke admin privileges"
    echo "5. Exit"
    echo -n "Select an option: "
    read choice

    case $choice in
        1)
            echo -n "Enter player IGN: "
            read ign
            whitelist_player "$ign"
            ;;
        2)
            echo -n "Enter player IGN: "
            read ign
            remove_from_whitelist "$ign"
            ;;
        3)
            echo -n "Enter user email: "
            read email
            grant_admin "$email"
            ;;
        4)
            echo -n "Enter user email: "
            read email
            revoke_admin "$email"
            ;;
        5)
            echo "Exiting..."
            exit 0
            ;;
        *)
            echo "Invalid option. Please try again."
            ;;
    esac
done
