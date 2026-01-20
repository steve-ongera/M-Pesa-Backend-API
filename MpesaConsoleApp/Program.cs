using System;
using System.Net.Http;
using System.Net.Http.Headers;
using System.Text;
using System.Threading.Tasks;
using Newtonsoft.Json;

public class MpesaClient
{
    private readonly HttpClient _client;
    private string _token;
    private string _userName;
    private decimal _currentBalance;

    public MpesaClient()
    {
        _client = new HttpClient();
        _client.BaseAddress = new Uri("http://localhost:8000/api/");
        _client.DefaultRequestHeaders.Accept.Add(
            new MediaTypeWithQualityHeaderValue("application/json")
        );
    }

    public async Task<bool> Login(string phoneNumber, string pin)
    {
        try
        {
            var data = new { phone_number = phoneNumber, pin = pin };
            var content = new StringContent(JsonConvert.SerializeObject(data), Encoding.UTF8, "application/json");
            var response = await _client.PostAsync("auth/login/", content);
            var result = await response.Content.ReadAsStringAsync();

            if (!response.IsSuccessStatusCode)
            {
                Console.WriteLine($"\n❌ Login failed: {result}");
                return false;
            }

            var loginResult = JsonConvert.DeserializeObject<dynamic>(result);
            if (loginResult.token == null)
            {
                Console.WriteLine("\n❌ Login failed: token not returned by API.");
                return false;
            }

            _token = loginResult.token;
            _userName = loginResult.user.full_name;

            _client.DefaultRequestHeaders.Authorization =
                new AuthenticationHeaderValue("Token", _token);

            // Get initial balance
            await GetBalance();

            return true;
        }
        catch (Exception ex)
        {
            Console.WriteLine($"\n❌ Error during login: {ex.Message}");
            return false;
        }
    }

    public async Task<decimal> GetBalance()
    {
        try
        {
            var response = await _client.GetAsync("transactions/balance/");
            var result = await response.Content.ReadAsStringAsync();

            if (!response.IsSuccessStatusCode)
            {
                Console.WriteLine($"\n❌ Failed to fetch balance: {result}");
                return 0;
            }

            var balanceData = JsonConvert.DeserializeObject<dynamic>(result);
            decimal balance = 0;
            decimal.TryParse(Convert.ToString(balanceData.balance), out balance);
            _currentBalance = balance;
            return balance;
        }
        catch (Exception ex)
        {
            Console.WriteLine($"\n❌ Error fetching balance: {ex.Message}");
            return 0;
        }
    }

    public async Task<bool> SendMoney(string receiverPhone, decimal amount, string description = "")
    {
        try
        {
            var data = new
            {
                receiver_phone = receiverPhone,
                amount = amount,
                description = description
            };
            var content = new StringContent(JsonConvert.SerializeObject(data), Encoding.UTF8, "application/json");
            var response = await _client.PostAsync("transactions/send_money/", content);
            var result = await response.Content.ReadAsStringAsync();

            if (!response.IsSuccessStatusCode)
            {
                var errorData = JsonConvert.DeserializeObject<dynamic>(result);
                if (errorData.error != null)
                {
                    Console.WriteLine($"\n❌ Send money failed: {errorData.error}");
                }
                else
                {
                    Console.WriteLine($"\n❌ Send money failed: {result}");
                }
                return false;
            }

            var transactionData = JsonConvert.DeserializeObject<dynamic>(result);
            _currentBalance = transactionData.new_balance;

            Console.WriteLine($"\n✅ {transactionData.message}");
            Console.WriteLine($"   Transaction Code: {transactionData.transaction.transaction_code}");
            Console.WriteLine($"   Amount Sent: KSh {amount:N2}");
            Console.WriteLine($"   New Balance: KSh {_currentBalance:N2}");

            return true;
        }
        catch (Exception ex)
        {
            Console.WriteLine($"\n❌ Error sending money: {ex.Message}");
            return false;
        }
    }

    public async Task<bool> Deposit(decimal amount, string description = "Deposit")
    {
        try
        {
            var data = new
            {
                amount = amount,
                description = description
            };
            var content = new StringContent(JsonConvert.SerializeObject(data), Encoding.UTF8, "application/json");
            var response = await _client.PostAsync("transactions/deposit/", content);
            var result = await response.Content.ReadAsStringAsync();

            if (!response.IsSuccessStatusCode)
            {
                Console.WriteLine($"\n❌ Deposit failed: {result}");
                return false;
            }

            var transactionData = JsonConvert.DeserializeObject<dynamic>(result);
            _currentBalance = transactionData.new_balance;

            Console.WriteLine($"\n✅ {transactionData.message}");
            Console.WriteLine($"   Transaction Code: {transactionData.transaction.transaction_code}");
            Console.WriteLine($"   Amount Deposited: KSh {amount:N2}");
            Console.WriteLine($"   New Balance: KSh {_currentBalance:N2}");

            return true;
        }
        catch (Exception ex)
        {
            Console.WriteLine($"\n❌ Error depositing money: {ex.Message}");
            return false;
        }
    }

    public async Task<bool> Withdraw(decimal amount, string description = "Withdrawal")
    {
        try
        {
            var data = new
            {
                amount = amount,
                description = description
            };
            var content = new StringContent(JsonConvert.SerializeObject(data), Encoding.UTF8, "application/json");
            var response = await _client.PostAsync("transactions/withdraw/", content);
            var result = await response.Content.ReadAsStringAsync();

            if (!response.IsSuccessStatusCode)
            {
                var errorData = JsonConvert.DeserializeObject<dynamic>(result);
                if (errorData.error != null)
                {
                    Console.WriteLine($"\n❌ Withdrawal failed: {errorData.error}");
                }
                else
                {
                    Console.WriteLine($"\n❌ Withdrawal failed: {result}");
                }
                return false;
            }

            var transactionData = JsonConvert.DeserializeObject<dynamic>(result);
            _currentBalance = transactionData.new_balance;

            Console.WriteLine($"\n✅ {transactionData.message}");
            Console.WriteLine($"   Transaction Code: {transactionData.transaction.transaction_code}");
            Console.WriteLine($"   Amount Withdrawn: KSh {amount:N2}");
            Console.WriteLine($"   New Balance: KSh {_currentBalance:N2}");

            return true;
        }
        catch (Exception ex)
        {
            Console.WriteLine($"\n❌ Error withdrawing money: {ex.Message}");
            return false;
        }
    }

    public async Task ShowTransactionHistory()
    {
        try
        {
            var response = await _client.GetAsync("transactions/history/");
            var result = await response.Content.ReadAsStringAsync();

            if (!response.IsSuccessStatusCode)
            {
                Console.WriteLine($"\n❌ Failed to fetch history: {result}");
                return;
            }

            var transactions = JsonConvert.DeserializeObject<dynamic>(result);

            Console.WriteLine("\n" + new string('=', 80));
            Console.WriteLine("TRANSACTION HISTORY (Last 20)");
            Console.WriteLine(new string('=', 80));

            if (transactions.Count == 0)
            {
                Console.WriteLine("No transactions found.");
            }
            else
            {
                foreach (var txn in transactions)
                {
                    Console.WriteLine($"\nCode: {txn.transaction_code}");
                    Console.WriteLine($"Type: {txn.transaction_type} | Status: {txn.status}");
                    Console.WriteLine($"Amount: KSh {txn.amount:N2}");

                    if (txn.sender_phone != null)
                        Console.WriteLine($"From: {txn.sender_phone}");
                    if (txn.receiver_phone != null)
                        Console.WriteLine($"To: {txn.receiver_phone}");

                    Console.WriteLine($"Date: {txn.created_at}");

                    if (!string.IsNullOrEmpty(Convert.ToString(txn.description)))
                        Console.WriteLine($"Description: {txn.description}");

                    Console.WriteLine(new string('-', 80));
                }
            }
        }
        catch (Exception ex)
        {
            Console.WriteLine($"\n❌ Error fetching history: {ex.Message}");
        }
    }

    public string GetUserName() => _userName;
    public decimal GetCurrentBalance() => _currentBalance;
}

class Program
{
    static async Task Main(string[] args)
    {
        var client = new MpesaClient();

        Console.Clear();
        Console.WriteLine(new string('=', 80));
        Console.WriteLine("                    M-PESA MOBILE MONEY CONSOLE APP");
        Console.WriteLine(new string('=', 80));
        Console.WriteLine();

        // Login
        Console.Write("Enter phone number (+254...): ");
        string phone = Console.ReadLine()?.Trim();
        Console.Write("Enter PIN: ");
        string pin = ReadPassword();
        Console.WriteLine();

        try
        {
            bool loggedIn = await client.Login(phone, pin);

            if (!loggedIn)
            {
                Console.WriteLine("\n❌ Login failed. Please try again.");
                Console.WriteLine("\nPress any key to exit...");
                Console.ReadKey();
                return;
            }

            Console.WriteLine($"\n✅ Login successful! Welcome, {client.GetUserName()}");

            // Main menu loop
            await ShowMainMenu(client);
        }
        catch (Exception ex)
        {
            Console.WriteLine($"\n❌ Unexpected error: {ex.Message}");
        }

        Console.WriteLine("\n\nThank you for using M-Pesa!");
        Console.WriteLine("Press any key to exit...");
        Console.ReadKey();
    }

    static async Task ShowMainMenu(MpesaClient client)
    {
        bool running = true;

        while (running)
        {
            Console.Clear();
            Console.WriteLine(new string('=', 80));
            Console.WriteLine($"                         MAIN MENU - {client.GetUserName()}");
            Console.WriteLine(new string('=', 80));
            Console.WriteLine($"\nCurrent Balance: KSh {client.GetCurrentBalance():N2}\n");
            Console.WriteLine("1. Send Money");
            Console.WriteLine("2. Withdraw Money");
            Console.WriteLine("3. Deposit Money");
            Console.WriteLine("4. Check Balance");
            Console.WriteLine("5. Transaction History");
            Console.WriteLine("6. Logout");
            Console.WriteLine(new string('=', 80));
            Console.Write("\nSelect an option (1-6): ");

            string choice = Console.ReadLine()?.Trim();

            switch (choice)
            {
                case "1":
                    await SendMoneyMenu(client);
                    break;
                case "2":
                    await WithdrawMoneyMenu(client);
                    break;
                case "3":
                    await DepositMoneyMenu(client);
                    break;
                case "4":
                    await CheckBalanceMenu(client);
                    break;
                case "5":
                    await client.ShowTransactionHistory();
                    Console.WriteLine("\nPress any key to continue...");
                    Console.ReadKey();
                    break;
                case "6":
                    running = false;
                    break;
                default:
                    Console.WriteLine("\n❌ Invalid option. Please try again.");
                    System.Threading.Thread.Sleep(1500);
                    break;
            }
        }
    }

    static async Task SendMoneyMenu(MpesaClient client)
    {
        Console.WriteLine("\n" + new string('-', 80));
        Console.WriteLine("SEND MONEY");
        Console.WriteLine(new string('-', 80));

        Console.Write("Enter receiver's phone number (+254...): ");
        string receiverPhone = Console.ReadLine()?.Trim();

        Console.Write("Enter amount (KSh): ");
        if (!decimal.TryParse(Console.ReadLine(), out decimal amount))
        {
            Console.WriteLine("❌ Invalid amount.");
            Console.WriteLine("\nPress any key to continue...");
            Console.ReadKey();
            return;
        }

        Console.Write("Enter description (optional): ");
        string description = Console.ReadLine()?.Trim();

        Console.Write($"\nConfirm sending KSh {amount:N2} to {receiverPhone}? (Y/N): ");
        if (Console.ReadLine()?.Trim().ToUpper() == "Y")
        {
            await client.SendMoney(receiverPhone, amount, description);
        }
        else
        {
            Console.WriteLine("\n❌ Transaction cancelled.");
        }

        Console.WriteLine("\nPress any key to continue...");
        Console.ReadKey();
    }

    static async Task WithdrawMoneyMenu(MpesaClient client)
    {
        Console.WriteLine("\n" + new string('-', 80));
        Console.WriteLine("WITHDRAW MONEY");
        Console.WriteLine(new string('-', 80));

        Console.Write("Enter amount to withdraw (KSh): ");
        if (!decimal.TryParse(Console.ReadLine(), out decimal amount))
        {
            Console.WriteLine("❌ Invalid amount.");
            Console.WriteLine("\nPress any key to continue...");
            Console.ReadKey();
            return;
        }

        Console.Write("Enter description (optional): ");
        string description = Console.ReadLine()?.Trim();

        Console.Write($"\nConfirm withdrawal of KSh {amount:N2}? (Y/N): ");
        if (Console.ReadLine()?.Trim().ToUpper() == "Y")
        {
            await client.Withdraw(amount, string.IsNullOrEmpty(description) ? "ATM Withdrawal" : description);
        }
        else
        {
            Console.WriteLine("\n❌ Transaction cancelled.");
        }

        Console.WriteLine("\nPress any key to continue...");
        Console.ReadKey();
    }

    static async Task DepositMoneyMenu(MpesaClient client)
    {
        Console.WriteLine("\n" + new string('-', 80));
        Console.WriteLine("DEPOSIT MONEY");
        Console.WriteLine(new string('-', 80));

        Console.Write("Enter amount to deposit (KSh): ");
        if (!decimal.TryParse(Console.ReadLine(), out decimal amount))
        {
            Console.WriteLine("❌ Invalid amount.");
            Console.WriteLine("\nPress any key to continue...");
            Console.ReadKey();
            return;
        }

        Console.Write("Enter description (optional): ");
        string description = Console.ReadLine()?.Trim();

        Console.Write($"\nConfirm deposit of KSh {amount:N2}? (Y/N): ");
        if (Console.ReadLine()?.Trim().ToUpper() == "Y")
        {
            await client.Deposit(amount, string.IsNullOrEmpty(description) ? "Cash Deposit" : description);
        }
        else
        {
            Console.WriteLine("\n❌ Transaction cancelled.");
        }

        Console.WriteLine("\nPress any key to continue...");
        Console.ReadKey();
    }

    static async Task CheckBalanceMenu(MpesaClient client)
    {
        Console.WriteLine("\n" + new string('-', 80));
        Console.WriteLine("BALANCE INQUIRY");
        Console.WriteLine(new string('-', 80));

        decimal balance = await client.GetBalance();
        Console.WriteLine($"\n💰 Your current balance is: KSh {balance:N2}");

        Console.WriteLine("\nPress any key to continue...");
        Console.ReadKey();
    }

    // Helper method to read password (hides input)
    static string ReadPassword()
    {
        string password = "";
        ConsoleKeyInfo key;

        do
        {
            key = Console.ReadKey(true);

            if (key.Key != ConsoleKey.Backspace && key.Key != ConsoleKey.Enter)
            {
                password += key.KeyChar;
                Console.Write("*");
            }
            else if (key.Key == ConsoleKey.Backspace && password.Length > 0)
            {
                password = password.Substring(0, password.Length - 1);
                Console.Write("\b \b");
            }
        }
        while (key.Key != ConsoleKey.Enter);

        return password;
    }
}